import { useState } from 'react'
import { FileDown, CheckCircle2 } from 'lucide-react'
import { getHealth, CASO_POC } from './api'
import type { DiagnoseResponse, PolicyResponse, ArtifactsResponse } from './types'

import { Vector3D } from './components/Vector3D'
import { PoliticaPanel } from './components/PoliticaPanel'
import { VerificacionTecnica } from './components/VerificacionTecnica'
import { Wizard } from './components/Wizard'
import type { DiagnosePayload } from './api'

type Tab = 'wizard' | 'resultados'

function App() {
  const [tab, setTab] = useState<Tab>('wizard')
  const [diag, setDiag] = useState<DiagnoseResponse | null>(null)
  const [policy, setPolicy] = useState<PolicyResponse | null>(null)
  const [artifacts, setArtifacts] = useState<ArtifactsResponse | null>(null)
  const [health, setHealth] = useState<{ modo?: string; modelo?: string } | null>(null)
  const [payload, setPayload] = useState<DiagnosePayload | null>(null)
  const [cargandoPolitica, setCargandoPolitica] = useState(false)
  const [cargandoArtefactos, setCargandoArtefactos] = useState(false)
  const [capacidad, setCapacidad] = useState<'pendiente' | 'propia' | 'asistida'>('pendiente')

  // Al completar el wizard o cargar POC, mostrar resultados
  const onDiagnosticoListo = (p: DiagnosePayload, d: DiagnoseResponse) => {
    setPayload(p)
    setDiag(d)
    setPolicy(null)
    setArtifacts(null)
    setCapacidad('pendiente')
    setTab('resultados')
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-white font-bold">IA</div>
          <div>
            <h1 className="text-lg font-semibold">Playbook de IA Responsable</h1>
            <p className="text-xs text-slate-500">Autodiagnóstico de gobernanza de IA para PYMES</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {health && (
            <span className={`text-xs px-2 py-1 rounded-full ${health.modo === 'completo' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
              {health.modo} · {health.modelo}
            </span>
          )}
          <button
            onClick={async () => setHealth(await getHealth())}
            className="text-xs text-slate-500 hover:text-slate-700"
          >
            estado
          </button>
        </div>
      </header>

      <nav className="bg-white border-b border-slate-200 px-6 flex gap-1">
        <button
          onClick={() => setTab('wizard')}
          className={`px-4 py-3 text-sm font-medium border-b-2 ${tab === 'wizard' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500'}`}
        >
          1. Asistente
        </button>
        <button
          onClick={() => setTab('resultados')}
          disabled={!diag}
          className={`px-4 py-3 text-sm font-medium border-b-2 disabled:opacity-40 ${tab === 'resultados' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-slate-500'}`}
        >
          2. Resultados
        </button>
      </nav>

      <main className="px-6 py-6">
        {tab === 'wizard' && (
          <Wizard
            onComplete={onDiagnosticoListo}
            onCargarPOC={async () => {
              const { diagnose } = await import('./api')
              const d = await diagnose(CASO_POC)
              onDiagnosticoListo(CASO_POC, d)
            }}
          />
        )}
        {tab === 'resultados' && diag && payload && (
          <ResultadosView
            diag={diag}
            payload={payload}
            policy={policy}
            artifacts={artifacts}
            capacidad={capacidad}
            setCapacidad={setCapacidad}
            onGenerarPolitica={async () => {
              setCargandoPolitica(true)
              try {
                const { generatePolicy } = await import('./api')
                const p = await generatePolicy({
                  bifurcacion: payload.bifurcacion,
                  sector: payload.sector,
                  pais: payload.pais,
                  brechas: diag.capa2.map(r => ({ id_control: r.id_control, brecha: r.brecha, nombre: r.brecha, nist: r.nist })),
                  faithfulness: true,
                })
                setPolicy(p)
              } catch (e) {
                setPolicy({ abstain: true, mensaje: `Error: ${e}` })
              } finally {
                setCargandoPolitica(false)
              }
            }}
            onGenerarArtefactos={async () => {
              setCargandoArtefactos(true)
              try {
                const { getArtifacts } = await import('./api')
                const a = await getArtifacts({ ...payload, generar_politica: false })
                setArtifacts(a)
              } catch (e) {
                console.error(e)
              } finally {
                setCargandoArtefactos(false)
              }
            }}
            cargandoPolitica={cargandoPolitica}
            cargandoArtefactos={cargandoArtefactos}
          />
        )}
      </main>
    </div>
  )
}

function ResultadosView({ diag, payload, policy, artifacts, capacidad, setCapacidad, onGenerarPolitica, onGenerarArtefactos, cargandoPolitica, cargandoArtefactos }: {
  diag: DiagnoseResponse
  payload: DiagnosePayload
  policy: PolicyResponse | null
  artifacts: ArtifactsResponse | null
  capacidad: 'pendiente' | 'propia' | 'asistida'
  setCapacidad: (c: 'pendiente' | 'propia' | 'asistida') => void
  onGenerarPolitica: () => void
  onGenerarArtefactos: () => void
  cargandoPolitica: boolean
  cargandoArtefactos: boolean
}) {
  const [subtab, setSubtab] = useState<'vector' | 'politica' | 'verificacion' | 'artefactos'>('vector')
  const asistida = capacidad === 'asistida'
  return (
    <div>
      <div className="flex gap-2 mb-4 flex-wrap">
        <button onClick={() => setSubtab('vector')} className={`px-3 py-2 rounded-lg text-sm ${subtab === 'vector' ? 'bg-indigo-600 text-white' : 'bg-white border'}`}>Informe</button>
        {asistida && (
          <>
            <button onClick={() => setSubtab('politica')} className={`px-3 py-2 rounded-lg text-sm ${subtab === 'politica' ? 'bg-indigo-600 text-white' : 'bg-white border'}`}>Política</button>
            <button onClick={() => setSubtab('verificacion')} className={`px-3 py-2 rounded-lg text-sm ${subtab === 'verificacion' ? 'bg-indigo-600 text-white' : 'bg-white border'}`}>Verificación técnica</button>
            <button onClick={() => setSubtab('artefactos')} className={`px-3 py-2 rounded-lg text-sm ${subtab === 'artefactos' ? 'bg-indigo-600 text-white' : 'bg-white border'}`}>Artefactos</button>
          </>
        )}
      </div>
      {subtab === 'vector' && (
        <>
          <div className="mb-4 flex justify-end">
            <button
              onClick={async () => {
                const res = await fetch('/api/informe', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(payload),
                })
                if (!res.ok) { console.error('Error generando PDF'); return }
                const blob = await res.blob()
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = 'informe_autodiagnostico_IA.pdf'
                a.click()
                URL.revokeObjectURL(url)
              }}
              className="inline-flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
            >
              <FileDown className="w-4 h-4" />
              Descargar informe PDF
            </button>
          </div>
          <Vector3D diag={diag.capa1} recs={diag.capa2} />

          {/* Card de decisión: ¿puede implementar por su cuenta? */}
          {capacidad === 'pendiente' && (
            <div className="mt-6 bg-white rounded-xl border border-indigo-200 p-6">
              <h2 className="text-lg font-semibold text-slate-800">¿Cómo desea proceder?</h2>
              <p className="text-sm text-slate-600 mt-2">
                El informe contiene todo lo que su organización necesita para implementar las mejoras.
                Si su equipo tiene la capacidad, puede proceder por su cuenta. Si no, el sistema puede
                generar una <strong>política de IA a la medida</strong> y un <strong>plan accionable</strong>
                {' '}para facilitar la implementación.
              </p>
              <div className="flex gap-3 mt-4 flex-wrap">
                <button
                  onClick={() => setCapacidad('propia')}
                  className="inline-flex items-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors"
                >
                  Mi equipo puede implementarlo
                </button>
                <button
                  onClick={() => { setCapacidad('asistida'); setSubtab('politica') }}
                  className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
                >
                  Necesito ayuda para implementar
                </button>
              </div>
            </div>
          )}

          {/* Mensaje de cierre si elige implementar por su cuenta */}
          {capacidad === 'propia' && (
            <div className="mt-6 bg-white rounded-xl border border-emerald-200 p-6">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <h2 className="text-base font-semibold text-slate-800">Perfecto</h2>
                  <p className="text-sm text-slate-600 mt-1">
                    Descargue el informe PDF y proceda con su equipo. Si más adelante necesita asistencia,
                    puede solicitarla aquí.
                  </p>
                  <button
                    onClick={() => { setCapacidad('asistida'); setSubtab('politica') }}
                    className="mt-3 text-sm text-indigo-600 hover:text-indigo-700 underline"
                  >
                    Solicitar asistencia ahora
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      )}
      {subtab === 'politica' && (
        <PoliticaPanel
          policy={policy}
          cargando={cargandoPolitica}
          onGenerar={onGenerarPolitica}
        />
      )}
      {subtab === 'verificacion' && (
        <VerificacionTecnica policy={policy} />
      )}
      {subtab === 'artefactos' && (
        <ArtefactosPanel artifacts={artifacts} cargando={cargandoArtefactos} onGenerar={onGenerarArtefactos} />
      )}
    </div>
  )
}

function ArtefactosPanel({ artifacts, cargando, onGenerar }: { artifacts: ArtifactsResponse | null; cargando: boolean; onGenerar: () => void }) {
  if (cargando) {
    return (
      <div className="bg-white rounded-xl border p-6 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-3"></div>
        <p className="text-sm text-slate-600">Generando artefactos…</p>
      </div>
    )
  }
  if (!artifacts) {
    return (
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-lg font-semibold mb-2">Plan accionable + Constancia verificable</h2>
        <p className="text-sm text-slate-600 mb-4">Genera el plan de implementación accionable (3.5) y la constancia verificable (3.6) — activos descargables que la PYME puede presentar a clientes y auditorías.</p>
        <button onClick={onGenerar} className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm">Generar artefactos</button>
      </div>
    )
  }
  const download = (filename: string, content: string, type = 'text/markdown') => {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = filename; a.click()
    URL.revokeObjectURL(url)
  }
  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border p-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Plan de implementación accionable (3.5)</h2>
          <button onClick={() => download('plan_accionable.md', artifacts.plan_markdown)} className="text-xs bg-slate-100 px-3 py-1.5 rounded-lg">Descargar .md</button>
        </div>
        <p className="text-sm text-slate-600 mb-3">{artifacts.plan.resumen.n_tareas} tareas · {artifacts.plan.resumen.n_quick_wins_0_30} quick wins (0-30 días) · {artifacts.plan.resumen.n_mediano_plazo_30_90} mediano plazo · {artifacts.plan.resumen.n_estructural} estructural</p>
        <div className="space-y-3">
          {Object.entries(artifacts.plan.fases).map(([fase, tareas]) => tareas.length > 0 && (
            <div key={fase}>
              <h3 className="font-medium text-sm mb-2">Fase {fase}</h3>
              <div className="space-y-2">
                {tareas.map((t, i) => (
                  <div key={i} className="border rounded-lg p-3 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{t.control} — {t.brecha}</span>
                      <span className="text-xs text-slate-500">prioridad {t.prioridad}</span>
                    </div>
                    <p className="text-slate-600 mt-1">{t.accion}</p>
                    <p className="text-xs text-slate-500 mt-1">Responsable: {t.responsable} · Cierre: {t.criterio_cierre}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="bg-white rounded-xl border p-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Constancia verificable (3.6)</h2>
          <button onClick={() => download('constancia.md', artifacts.constancia_markdown)} className="text-xs bg-slate-100 px-3 py-1.5 rounded-lg">Descargar .md</button>
        </div>
        <pre className="text-xs whitespace-pre-wrap bg-slate-50 p-4 rounded-lg max-h-96 overflow-auto">{artifacts.constancia_markdown}</pre>
      </div>
    </div>
  )
}

export default App
