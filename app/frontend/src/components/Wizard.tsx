import { useEffect, useState } from 'react'
import { Loader2, AlertTriangle, ChevronLeft, ChevronRight, Paperclip, X, CheckCircle2 } from 'lucide-react'
import type { DiagnosePayload, EvidenceAnalysis } from '../api'
import { analyzeEvidence, diagnose, getQuestions } from '../api'
import type { ArbolPreguntas, DiagnoseResponse, Pregunta, Subpregunta, ValorRespuesta } from '../types'

const PAISES = [
  { valor: '', etiqueta: 'Global (marcos universales)', activo: true },
  { valor: 'CO', etiqueta: 'Colombia', activo: false },
  { valor: 'MX', etiqueta: 'México', activo: false },
  { valor: 'AR', etiqueta: 'Argentina', activo: false },
  { valor: 'BR', etiqueta: 'Brasil', activo: false },
  { valor: 'CL', etiqueta: 'Chile', activo: false },
  { valor: 'PE', etiqueta: 'Perú', activo: false },
]

const SECTORES = [
  { categoria: 'Servicios', items: ['Comercio/Retail', 'Salud', 'Educación', 'Hostelería/Turismo', 'Medios/Comunicación', 'Servicios profesionales', 'Transporte/Logística'] },
  { categoria: 'Industria', items: ['Manufactura', 'Construcción', 'Agricultura/Agro', 'Minería/Energía'] },
  { categoria: 'Tecnología', items: ['Tecnología/Software', 'Telecomunicaciones'] },
  { categoria: 'Financiero', items: ['Financiero/Bancario', 'Seguros'] },
  { categoria: 'Otros', items: ['Sector público', 'Otro'] },
]

const STEPS = ['Contexto', 'Bifurcación', 'Árbol', 'Resultados']

function subpreguntaActiva(sub: Subpregunta, respuestas: Record<string, ValorRespuesta>): boolean {
  if (!sub.condicion) return true
  const val = respuestas[sub.condicion.pregunta]
  const en = sub.condicion.en
  if (Array.isArray(val)) {
    if (sub.condicion.modo === 'todas') return en.every((e) => val.includes(e))
    return val.some((v) => en.includes(v))
  }
  if (val === undefined || val === null || val === '') return false
  return en.includes(String(val))
}

function tramoDeNumero(tramos: { hasta: number | null; etiqueta: string }[], valor: number | undefined): string {
  if (valor === undefined) return ''
  for (const t of tramos) {
    if (t.hasta === null || valor <= t.hasta) return t.etiqueta
  }
  return tramos[tramos.length - 1]?.etiqueta || ''
}

export function Wizard({ onComplete, onCargarPOC }: {
  onComplete: (p: DiagnosePayload, d: DiagnoseResponse) => void
  onCargarPOC: () => void
}) {
  const [paso, setPaso] = useState(0)
  const [pais, setPais] = useState<string | null>(null)
  const [sector, setSector] = useState<string | null>(null)
  const [bifurcacion, setBifurcacion] = useState<string>('')
  const [respuestas, setRespuestas] = useState<Record<string, ValorRespuesta>>({})
  const [evidencias, setEvidencias] = useState<string[]>([])
  const [nombresEvidencia, setNombresEvidencia] = useState<Record<string, string>>({})
  const [analisisEvidencia, setAnalisisEvidencia] = useState<Record<string, EvidenceAnalysis>>({})
  const [cargandoAnalisis, setCargandoAnalisis] = useState<Record<string, boolean>>({})
  const [arbol, setArbol] = useState<ArbolPreguntas | null>(null)
  const [cargandoArbol, setCargandoArbol] = useState(true)
  const [errorCarga, setErrorCarga] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)
  const [errorEnvio, setErrorEnvio] = useState<string | null>(null)

  useEffect(() => {
    let vivo = true
    ;(async () => {
      try {
        const a = await getQuestions()
        if (vivo) {
          setArbol(a)
          setCargandoArbol(false)
        }
      } catch (e) {
        if (vivo) {
          setErrorCarga(e instanceof Error ? e.message : 'Error cargando el árbol')
          setCargandoArbol(false)
        }
      }
    })()
    return () => {
      vivo = false
    }
  }, [])

  const preguntasAplicables = arbol
    ? arbol.preguntas.filter((p) => !p.ramas || p.ramas.includes(bifurcacion))
    : []

  const idsAplicables = new Set(preguntasAplicables.map((p) => p.id))
  const respondidas = Object.keys(respuestas).filter((id) => idsAplicables.has(id) && respuestas[id] !== '' && respuestas[id] !== undefined)
  const totalAplicables = preguntasAplicables.length
  const suficientes = respondidas.length > 0 && respondidas.length >= Math.ceil(totalAplicables / 2)

  const setRespuesta = (id: string, valor: ValorRespuesta) => {
    setRespuestas((r) => ({ ...r, [id]: valor }))
  }

  const adjuntarEvidencia = async (id: string, archivo: File | null) => {
    if (!archivo) return
    setNombresEvidencia((n) => ({ ...n, [id]: archivo.name }))
    setCargandoAnalisis((c) => ({ ...c, [id]: true }))
    try {
      const resultado = await analyzeEvidence(id, archivo)
      setAnalisisEvidencia((a) => ({ ...a, [id]: resultado }))
      if (!resultado.error && resultado.score >= 0.2) {
        setEvidencias((e) => (e.includes(id) ? e : [...e, id]))
      }
    } catch (e) {
      console.error(e)
      setAnalisisEvidencia((a) => ({ ...a, [id]: { error: 'No se pudo analizar' } as EvidenceAnalysis }))
    } finally {
      setCargandoAnalisis((c) => ({ ...c, [id]: false }))
    }
  }

  const removerEvidencia = (id: string) => {
    setEvidencias((e) => e.filter((x) => x !== id))
    setNombresEvidencia((n) => {
      const copia = { ...n }
      delete copia[id]
      return copia
    })
    setAnalisisEvidencia((a) => {
      const copia = { ...a }
      delete copia[id]
      return copia
    })
  }

  const toggleMultipleSeleccion = (id: string, opcion: string, max?: number | null) => {
    setRespuestas((r) => {
      const actual = Array.isArray(r[id]) ? (r[id] as string[]) : []
      const existe = actual.includes(opcion)
      let nuevo: string[]
      if (existe) nuevo = actual.filter((x) => x !== opcion)
      else if (max && actual.length >= max) nuevo = [actual[actual.length - 1], opcion]
      else nuevo = [...actual, opcion]
      return { ...r, [id]: nuevo }
    })
  }

  const enviar = async () => {
    if (!arbol) return
    setPaso(3)
    setEnviando(true)
    setErrorEnvio(null)
    const payload: DiagnosePayload = {
      bifurcacion,
      respuestas,
      evidencias,
      pais,
      sector,
    }
    try {
      const resp = await diagnose(payload)
      setEnviando(false)
      onComplete(payload, resp)
    } catch (e) {
      setEnviando(false)
      setErrorEnvio(e instanceof Error ? e.message : 'Error generando diagnóstico')
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex justify-end mb-3">
        <button
          onClick={onCargarPOC}
          className="text-xs bg-white border border-slate-200 px-3 py-1.5 rounded-lg hover:border-indigo-400 hover:text-indigo-600 transition"
        >
          Cargar caso demo (POC)
        </button>
      </div>

      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          {STEPS.map((s, i) => (
            <div key={s} className="flex items-center flex-1 last:flex-none">
              <div className="flex items-center gap-2">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium border ${
                    i < paso
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : i === paso
                      ? 'bg-white text-indigo-600 border-indigo-600'
                      : 'bg-white text-slate-400 border-slate-200'
                  }`}
                >
                  {i < paso ? '✓' : i + 1}
                </div>
                <span className={`text-xs hidden sm:inline ${i === paso ? 'text-indigo-600 font-medium' : 'text-slate-400'}`}>
                  {s}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div className={`h-px flex-1 mx-2 ${i < paso ? 'bg-indigo-600' : 'bg-slate-200'}`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {cargandoArbol && paso < 3 && (
        <div className="bg-white rounded-xl border p-6 flex items-center gap-3 text-slate-600 text-sm">
          <Loader2 className="w-4 h-4 animate-spin" /> Cargando árbol de preguntas…
        </div>
      )}

      {errorCarga && paso < 3 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 flex items-start gap-3 text-red-700 text-sm">
          <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
          <div>
            <p className="font-medium mb-1">No se pudo cargar el árbol</p>
            <p className="text-xs">{errorCarga}</p>
          </div>
        </div>
      )}

      {!cargandoArbol && !errorCarga && arbol && paso === 0 && (
        <div className="bg-white rounded-xl border p-6">
          <h2 className="text-lg font-semibold mb-1">Contexto de la organización</h2>
          <p className="text-sm text-slate-600 mb-6">El diagnóstico usa marcos universales (NIST AI RMF, ISO 42001 y principios éticos UNESCO/OCDE). El país es opcional y solo afecta metadatos.</p>

          <div className="space-y-5">
            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1.5">País</label>
              <select
                value={pais ?? ''}
                onChange={(e) => setPais(e.target.value || null)}
                className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              >
                <option value="">Selecciona un país…</option>
                {PAISES.map((p) => (
                  <option key={p.valor} value={p.valor} disabled={!p.activo}>
                    {p.etiqueta}{p.activo ? '' : ' (próximamente)'}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1.5">Sector</label>
              <select
                value={sector ?? ''}
                onChange={(e) => setSector(e.target.value || null)}
                className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
              >
                <option value="">Selecciona un sector…</option>
                {SECTORES.map((grupo) => (
                  <optgroup key={grupo.categoria} label={grupo.categoria}>
                    {grupo.items.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </optgroup>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-6 flex items-center justify-between">
            <p className="text-xs text-slate-500">Marco normativo universal activo para cualquier jurisdicción.</p>
            <button
              onClick={() => setPaso(1)}
              disabled={!sector}
              className="inline-flex items-center gap-1.5 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-40 hover:bg-indigo-700 transition"
            >
              Siguiente <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {!cargandoArbol && !errorCarga && arbol && paso === 1 && (
        <div className="bg-white rounded-xl border p-6">
          <h2 className="text-xl font-semibold mb-2">{arbol.bifurcacion.texto}</h2>
          <p className="text-sm text-slate-600 mb-6">{arbol.bifurcacion.contexto_pyme}</p>

          <div className="space-y-3">
            {arbol.bifurcacion.opciones.map((o) => (
              <button
                key={o.valor}
                onClick={() => {
                  setBifurcacion(o.valor)
                  setPaso(2)
                }}
                className="w-full text-left border border-slate-200 rounded-lg p-4 hover:border-indigo-500 hover:bg-indigo-50/50 transition group"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm group-hover:text-indigo-700">{o.etiqueta}</p>
                    {o.puntaje !== null && o.puntaje !== undefined && (
                      <p className="text-xs text-slate-500 mt-1">{o.puntaje} pts</p>
                    )}
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600" />
                </div>
              </button>
            ))}
          </div>

          <div className="mt-6">
            <button
              onClick={() => setPaso(0)}
              className="inline-flex items-center gap-1.5 text-slate-600 text-sm hover:text-slate-900"
            >
              <ChevronLeft className="w-4 h-4" /> Atrás
            </button>
          </div>
        </div>
      )}

      {!cargandoArbol && !errorCarga && arbol && paso === 2 && (
        <PasoArbol
          preguntas={preguntasAplicables}
          respuestas={respuestas}
          setRespuesta={setRespuesta}
          toggleMultipleSeleccion={toggleMultipleSeleccion}
          evidencias={evidencias}
          adjuntarEvidencia={adjuntarEvidencia}
          removerEvidencia={removerEvidencia}
          nombresEvidencia={nombresEvidencia}
          respondidas={respondidas.length}
          total={totalAplicables}
          onAtras={() => setPaso(1)}
          onEnviar={enviar}
          puedenEnviar={suficientes}
        />
      )}

      {paso === 3 && (
        <div className="bg-white rounded-xl border p-8">
          {enviando ? (
            <div className="flex flex-col items-center gap-3 py-8">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
              <p className="text-sm text-slate-600">Generando diagnóstico…</p>
              <p className="text-xs text-slate-400">Esto puede tardar varios segundos.</p>
            </div>
          ) : errorEnvio ? (
            <div className="flex flex-col items-center gap-4 py-6">
              <AlertTriangle className="w-8 h-8 text-red-500" />
              <p className="text-sm text-red-700 font-medium">No se pudo generar el diagnóstico</p>
              <p className="text-xs text-slate-500 max-w-md text-center">{errorEnvio}</p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPaso(2)}
                  className="text-sm text-slate-600 hover:text-slate-900"
                >
                  Volver al árbol
                </button>
                <button
                  onClick={enviar}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700"
                >
                  Reintentar
                </button>
              </div>
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}

function PasoArbol({
  preguntas,
  respuestas,
  setRespuesta,
  toggleMultipleSeleccion,
  evidencias,
  adjuntarEvidencia,
  removerEvidencia,
  nombresEvidencia,
  respondidas,
  total,
  onAtras,
  onEnviar,
  puedenEnviar,
}: {
  preguntas: Pregunta[]
  respuestas: Record<string, ValorRespuesta>
  setRespuesta: (id: string, v: ValorRespuesta) => void
  toggleMultipleSeleccion: (id: string, opcion: string, max?: number | null) => void
  evidencias: string[]
  adjuntarEvidencia: (id: string, archivo: File | null) => void
  removerEvidencia: (id: string) => void
  nombresEvidencia: Record<string, string>
  respondidas: number
  total: number
  onAtras: () => void
  onEnviar: () => void
  puedenEnviar: boolean
}) {
  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border p-4 sticky top-2 z-10">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="text-slate-500">Pregunta {Math.min(respondidas + 1, total)} de {total}</span>
          <span className="text-slate-400">{respondidas}/{total} respondidas</span>
        </div>
        <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-600 transition-all"
            style={{ width: `${total ? (respondidas / total) * 100 : 0}%` }}
          />
        </div>
      </div>

      {preguntas.map((p, i) => (
        <PreguntaCard
          key={p.id}
          pregunta={p}
          index={i}
          respuesta={respuestas[p.id]}
          respuestas={respuestas}
          setRespuesta={setRespuesta}
          toggleMultipleSeleccion={toggleMultipleSeleccion}
          tieneEvidencia={evidencias.includes(p.id)}
          adjuntarEvidencia={adjuntarEvidencia}
          removerEvidencia={removerEvidencia}
          nombreEvidencia={nombresEvidencia[p.id]}
          analisis={analisisEvidencia[p.id]}
          cargandoAnalisis={cargandoAnalisis[p.id]}
        />
      ))}

      <div className="bg-white rounded-xl border p-4 flex items-center justify-between sticky bottom-2">
        <button
          onClick={onAtras}
          className="inline-flex items-center gap-1.5 text-slate-600 text-sm hover:text-slate-900"
        >
          <ChevronLeft className="w-4 h-4" /> Atrás
        </button>
        <button
          onClick={onEnviar}
          disabled={!puedenEnviar}
          className="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-medium disabled:opacity-40 hover:bg-indigo-700 transition"
        >
          Generar diagnóstico
        </button>
      </div>
    </div>
  )
}

function PreguntaCard({
  pregunta,
  index,
  respuesta,
  respuestas,
  setRespuesta,
  toggleMultipleSeleccion,
  tieneEvidencia,
  adjuntarEvidencia,
  removerEvidencia,
  nombreEvidencia,
  analisis,
  cargandoAnalisis,
}: {
  pregunta: Pregunta
  index: number
  respuesta: ValorRespuesta | undefined
  respuestas: Record<string, ValorRespuesta>
  setRespuesta: (id: string, v: ValorRespuesta) => void
  toggleMultipleSeleccion: (id: string, opcion: string, max?: number | null) => void
  tieneEvidencia: boolean
  adjuntarEvidencia: (id: string, archivo: File | null) => void
  removerEvidencia: (id: string) => void
  nombreEvidencia?: string
  analisis?: EvidenceAnalysis
  cargandoAnalisis?: boolean
}) {
  const filasMatriz = pregunta.filas_de ? (Number(respuestas[pregunta.filas_de]) || 0) : 0

  return (
    <div className="bg-white rounded-xl border p-6">
      <div className="flex items-start justify-between gap-3 mb-1">
        <h3 className="text-sm font-medium">
          <span className="text-slate-400 mr-1">{index + 1}.</span>
          {pregunta.texto}
        </h3>
        {cargandoAnalisis ? (
          <span className="inline-flex items-center gap-1.5 text-xs text-slate-500 shrink-0">
            <Loader2 className="w-3 h-3 animate-spin" /> Analizando…
          </span>
        ) : tieneEvidencia ? (
          <div className="flex items-center gap-2 shrink-0">
            <span className="inline-flex items-center gap-1.5 text-xs text-green-700 bg-green-50 rounded-full px-2.5 py-1">
              <CheckCircle2 className="w-3 h-3" />
              <span className="max-w-[120px] truncate">{nombreEvidencia || 'Archivo adjunto'}</span>
            </span>
            <button
              onClick={() => removerEvidencia(pregunta.id)}
              className="text-xs text-slate-400 hover:text-red-500"
              title="Quitar evidencia"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <label className="flex items-center gap-1.5 text-xs text-slate-500 cursor-pointer shrink-0 hover:text-indigo-600 transition-colors">
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.docx,.csv,.xlsx"
              className="hidden"
              onChange={(e) => adjuntarEvidencia(pregunta.id, e.target.files?.[0] ?? null)}
            />
            <Paperclip className="w-3 h-3" /> Adjuntar evidencia
          </label>
        )}
      </div>
      {analisis && (
        <div className={`mb-3 text-xs rounded-lg px-3 py-2 ${analisis.error ? 'bg-red-50 text-red-700' : analisis.score >= 0.2 ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'}`}>
          {analisis.error ? (
            <span>{analisis.error}</span>
          ) : (
            <span>
              Cobertura de evidencia: <strong>{Math.round(analisis.score * 100)}%</strong>{' '}
              ({analisis.encontradas}/{analisis.palabras_clave} conceptos clave).
              {analisis.coincidencias.length > 0 && (
                <> Coincidencias: {analisis.coincidencias.join(', ')}.</>
              )}
            </span>
          )}
        </div>
      )}
      {pregunta.contexto_pyme && (
        <p className="text-xs text-slate-500 mb-4">{pregunta.contexto_pyme}</p>
      )}

      <CuerpoPregunta
        pregunta={pregunta}
        respuesta={respuesta}
        respuestas={respuestas}
        setRespuesta={setRespuesta}
        toggleMultipleSeleccion={toggleMultipleSeleccion}
        filasMatriz={filasMatriz}
      />

      {pregunta.subpreguntas?.map((sub) =>
        subpreguntaActiva(sub, respuestas) ? (
          <div key={sub.id} className="mt-5 pl-4 border-l-2 border-indigo-100">
            <p className="text-sm font-medium mb-1">
              <span className="text-indigo-400 mr-1">↳</span>
              {sub.texto}
            </p>
            {sub.contexto_pyme && <p className="text-xs text-slate-500 mb-3">{sub.contexto_pyme}</p>}
            <CuerpoPregunta
              pregunta={sub as unknown as Pregunta}
              respuesta={respuestas[sub.id]}
              respuestas={respuestas}
              setRespuesta={setRespuesta}
              toggleMultipleSeleccion={toggleMultipleSeleccion}
              filasMatriz={0}
            />
            {sub.subpreguntas?.map((sub2) =>
              subpreguntaActiva(sub2, respuestas) ? (
                <div key={sub2.id} className="mt-4 pl-4 border-l-2 border-slate-100">
                  <p className="text-sm font-medium mb-1">{sub2.texto}</p>
                  {sub2.contexto_pyme && <p className="text-xs text-slate-500 mb-3">{sub2.contexto_pyme}</p>}
                  <CuerpoPregunta
                    pregunta={sub2 as unknown as Pregunta}
                    respuesta={respuestas[sub2.id]}
                    respuestas={respuestas}
                    setRespuesta={setRespuesta}
                    toggleMultipleSeleccion={toggleMultipleSeleccion}
                    filasMatriz={0}
                  />
                </div>
              ) : null
            )}
          </div>
        ) : null
      )}
    </div>
  )
}

function CuerpoPregunta({
  pregunta,
  respuesta,
  setRespuesta,
  toggleMultipleSeleccion,
  filasMatriz,
}: {
  pregunta: Pregunta
  respuesta: ValorRespuesta | undefined
  respuestas: Record<string, ValorRespuesta>
  setRespuesta: (id: string, v: ValorRespuesta) => void
  toggleMultipleSeleccion: (id: string, opcion: string, max?: number | null) => void
  filasMatriz: number
}) {
  const tipo = pregunta.tipo

  if (tipo === 'multiple' || tipo === 'likert' || tipo === 'estado') {
    const opciones = pregunta.opciones || []
    const actual = respuesta !== undefined ? String(respuesta) : ''
    return (
      <div className="grid sm:grid-cols-2 gap-2">
        {opciones.map((o) => {
          const seleccionada = actual === o.valor
          return (
            <button
              key={o.valor}
              onClick={() => setRespuesta(pregunta.id, o.valor)}
              className={`text-left border rounded-lg p-3 text-sm transition ${
                seleccionada
                  ? 'border-indigo-600 bg-indigo-50 text-indigo-700'
                  : 'border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/40'
              }`}
            >
              {o.etiqueta}
            </button>
          )
        })}
      </div>
    )
  }

  if (tipo === 'multiple_seleccion') {
    const opciones = pregunta.opciones || []
    const actual = Array.isArray(respuesta) ? (respuesta as string[]) : []
    return (
      <div className="space-y-2">
        {opciones.map((o) => {
          const sel = actual.includes(o.valor)
          return (
            <label
              key={o.valor}
              className={`flex items-center gap-2.5 border rounded-lg p-3 text-sm cursor-pointer transition ${
                sel ? 'border-indigo-600 bg-indigo-50' : 'border-slate-200 hover:border-indigo-400'
              }`}
            >
              <input
                type="checkbox"
                checked={sel}
                onChange={() => toggleMultipleSeleccion(pregunta.id, o.valor)}
                className="accent-indigo-600"
              />
              {o.etiqueta}
            </label>
          )
        })}
      </div>
    )
  }

  if (tipo === 'numero') {
    const valorNum = typeof respuesta === 'number' ? respuesta : undefined
    const tramos = pregunta.tramos || []
    const tramoActual = tramoDeNumero(tramos, valorNum)
    return (
      <div>
        <input
          type="number"
          min={0}
          value={valorNum ?? ''}
          onChange={(e) => setRespuesta(pregunta.id, e.target.value === '' ? 0 : Number(e.target.value))}
          className="w-32 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
        />
        {tramos.length > 0 && valorNum !== undefined && (
          <p className="mt-2 text-xs text-slate-500">
            Tramo: <span className="font-medium text-indigo-600">{tramoActual}</span>
          </p>
        )}
      </div>
    )
  }

  if (tipo === 'matriz') {
    const opciones = pregunta.opciones || []
    const filas = filasMatriz
    if (filas <= 0) {
      return <p className="text-xs text-amber-600">Primero indica el número de sistemas en la pregunta anterior.</p>
    }
    const arrActual = Array.isArray(respuesta) ? (respuesta as string[]) : []
    return (
      <div className="space-y-2">
        {Array.from({ length: filas }).map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            <span className="text-xs text-slate-500 w-20 shrink-0">Sistema {i + 1}</span>
            <select
              value={arrActual[i] ?? ''}
              onChange={(e) => {
                const copia = [...arrActual]
                while (copia.length < i + 1) copia.push('')
                copia[i] = e.target.value
                setRespuesta(pregunta.id, copia.filter((x) => x !== ''))
              }}
              className="flex-1 border border-slate-200 rounded-lg px-2.5 py-1.5 text-sm focus:outline-none focus:border-indigo-500"
            >
              <option value="">—</option>
              {opciones.map((o) => (
                <option key={o.valor} value={o.valor}>{o.etiqueta}</option>
              ))}
            </select>
          </div>
        ))}
      </div>
    )
  }

  if (tipo === 'texto') {
    const actual = respuesta !== undefined ? String(respuesta) : ''
    return (
      <textarea
        value={actual}
        onChange={(e) => setRespuesta(pregunta.id, e.target.value)}
        rows={3}
        className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
        placeholder="(no puntúa, solo contexto cualitativo)"
      />
    )
  }

  return <p className="text-xs text-slate-400">Tipo no soportado: {tipo}</p>
}