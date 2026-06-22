import Plot from 'react-plotly.js'
import type * as Plotly from 'plotly.js'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts'
import { AlertTriangle, Clock, FileText, ShieldAlert, Info, BookOpen, CheckCircle2 } from 'lucide-react'
import type { Diagnostico, Recomendacion } from '../types'

const FUNCIONES_NIST = ['GOVERN', 'MAP', 'MEASURE', 'MANAGE'] as const
const PRINCIPIOS = ['beneficencia', 'no_maleficencia', 'autonomia', 'justicia', 'explicabilidad'] as const

const ETIQUETA_PRINCIPIO: Record<string, string> = {
  beneficencia: 'Beneficencia',
  no_maleficencia: 'No maleficencia',
  autonomia: 'Autonomía',
  justicia: 'Justicia',
  explicabilidad: 'Explicabilidad',
}

const ETIQUETA_NIST: Record<string, string> = {
  GOVERN: 'Gobernar',
  MAP: 'Mapear',
  MEASURE: 'Medir',
  MANAGE: 'Gestionar',
}

const AREAS_ISO: { prefijo: string; nombre: string }[] = [
  { prefijo: 'A.2', nombre: 'Política' },
  { prefijo: 'A.3', nombre: 'Roles' },
  { prefijo: 'A.5', nombre: 'Evaluación de impacto' },
  { prefijo: 'A.6', nombre: 'Datos' },
  { prefijo: 'A.7', nombre: 'Documentación' },
  { prefijo: 'A.8', nombre: 'Operación' },
  { prefijo: 'A.9', nombre: 'Supervisión' },
  { prefijo: 'A.10', nombre: 'Terceros e incidentes' },
]

function colorScore(score: number): string {
  if (score < 40) return '#dc2626'
  if (score <= 70) return '#f59e0b'
  return '#16a34a'
}

function cubeMesh(s: number, color: string, opacity: number, name: string): Plotly.Data {
  return {
    type: 'mesh3d',
    x: [0, s, 0, s, 0, s, 0, s],
    y: [0, 0, s, s, 0, 0, s, s],
    z: [0, 0, 0, 0, s, s, s, s],
    i: [0, 0, 4, 4, 0, 0, 3, 3, 0, 0, 1, 1],
    j: [1, 2, 5, 6, 1, 5, 2, 6, 3, 7, 2, 6],
    k: [2, 3, 6, 7, 5, 4, 6, 7, 7, 4, 6, 5],
    color,
    opacity,
    name,
    showlegend: false,
    hoverinfo: 'skip',
  } as unknown as Plotly.Data
}

export function Vector3D({ diag, recs: _recs }: { diag: Diagnostico; recs: Recomendacion[] }) {
  const v = diag.diagnostico_vector
  const sinDatos = v.x_etico === null || v.y_iso === null || v.z_nist === null

  const score = sinDatos ? 0 : ((v.x_etico! + v.y_iso! + v.z_nist!) / 3)
  const colorPunto = colorScore(score)

  const traces3d: Plotly.Data[] = [
    cubeMesh(50, '#f59e0b', 0.06, 'Zona aceptable (50)'),
    cubeMesh(80, '#16a34a', 0.05, 'Zona óptima (80)'),
  ]

  if (!sinDatos) {
    traces3d.push({
      type: 'scatter3d',
      mode: 'markers+text',
      x: [v.x_etico as number],
      y: [v.y_iso as number],
      z: [v.z_nist as number],
      text: ['Tu organización'],
      textposition: 'top center',
      marker: { size: 16, color: colorPunto, line: { color: '#0f172a', width: 1.5 } },
      name: 'Tu organización',
    } as unknown as Plotly.Data)
  }

  const layout3d: Partial<Plotly.Layout> = {
    margin: { l: 0, r: 0, t: 0, b: 0 },
    height: 500,
    showlegend: false,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    scene: {
      xaxis: { title: { text: 'ÉTICO' }, range: [0, 100], dtick: 25 },
      yaxis: { title: { text: 'ISO' }, range: [0, 100], dtick: 25 },
      zaxis: { title: { text: 'NIST' }, range: [0, 100], dtick: 25 },
      aspectmode: 'cube',
      camera: { eye: { x: 1.6, y: 1.6, z: 1.1 } },
    },
  }

  const nistData = FUNCIONES_NIST.map((fn) => ({
    name: fn,
    value: diag.madurez_nist[fn] ?? 0,
  }))

  const isoData = AREAS_ISO.map((area) => {
    const controles = diag.cobertura_iso.filter((c) => c.id_control.startsWith(area.prefijo))
    const valor = controles.length > 0
      ? Math.round(controles.reduce((s, c) => s + (c.puntaje ?? 0), 0) / controles.length)
      : 0
    return { name: area.nombre, value: valor }
  })

  const eticaData = PRINCIPIOS.map((p) => {
    const raw = diag.principios_eticos[p]
    const falta = raw === null || raw === undefined
    return {
      name: falta ? `${ETIQUETA_PRINCIPIO[p]}*` : ETIQUETA_PRINCIPIO[p],
      value: falta ? 0 : raw,
    }
  })
  const eticaIncompleta = eticaData.some((d) => d.name.endsWith('*'))

  const gaps = diag.gap_register
  const nAltas = gaps.filter((g) => g.severidad === 'alta').length
  const nMedias = gaps.filter((g) => g.severidad === 'media').length
  const nBajas = gaps.filter((g) => g.severidad === 'baja').length

  const badgeSev = (sev: string): string => {
    if (sev === 'alta') return 'bg-red-100 text-red-700'
    if (sev === 'media') return 'bg-amber-100 text-amber-700'
    return 'bg-emerald-100 text-emerald-700'
  }

  const badgePlazo = (sev: string): string => {
    if (sev === 'alta') return 'bg-red-50 text-red-600 border-red-200'
    if (sev === 'media') return 'bg-amber-50 text-amber-600 border-amber-200'
    return 'bg-emerald-50 text-emerald-600 border-emerald-200'
  }

  const nivelVerif = diag.verificabilidad.nivel
  const verifColor = nivelVerif.includes('alto') ? 'text-emerald-600' : nivelVerif.includes('medio') ? 'text-amber-600' : 'text-slate-500'

  return (
    <div className="space-y-6">
      {/* Aclaración inicial — antes de cualquier gráfica */}
      <section className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-start gap-3 mb-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center shrink-0">
            <Info className="w-5 h-5 text-indigo-600" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-semibold">Diagnóstico de gobernanza de IA — Resumen para su organización</h2>
            <p className="text-sm text-slate-600 mt-1">
              Este diagnóstico evalúa el uso de IA de su organización frente a tres marcos normativos internacionales
              y los muestra en un <strong>vector tridimensional</strong> (ÉTICO · ISO · NIST), cada eje de 0 a 100.
            </p>
            <p className="text-sm text-slate-600 mt-2">
              A continuación encontrará: (1) una visión general del estado actual, (2) las brechas detectadas con su
              severidad y plazo recomendado de implementación, y (3) la fuente normativa exacta de cada control.
            </p>
          </div>
        </div>

        {/* Perfil + resumen rápido */}
        <div className="grid gap-3 sm:grid-cols-3 mt-4">
          <div className="bg-slate-50 rounded-lg p-3">
            <p className="text-xs text-slate-500 uppercase tracking-wide">Perfil</p>
            <p className="text-sm font-medium text-slate-800 mt-1">{diag.perfil.descripcion}</p>
          </div>
          <div className="bg-slate-50 rounded-lg p-3">
            <p className="text-xs text-slate-500 uppercase tracking-wide">Brechas detectadas</p>
            <p className="text-sm font-medium text-slate-800 mt-1">
              {gaps.length} en total · <span className="text-red-600">{nAltas} altas</span> · <span className="text-amber-600">{nMedias} medias</span> · <span className="text-emerald-600">{nBajas} bajas</span>
            </p>
          </div>
          <div className="bg-slate-50 rounded-lg p-3">
            <p className="text-xs text-slate-500 uppercase tracking-wide">Verificabilidad</p>
            <p className={`text-sm font-medium mt-1 ${verifColor}`}>
              {nivelVerif} ({diag.verificabilidad.con_evidencia}/{diag.verificabilidad.respondidas} resp. con evidencia)
            </p>
          </div>
        </div>

        {/* Lectura del vector */}
        {!sinDatos && (
          <div className="mt-4 p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg border border-indigo-100">
            <p className="text-sm text-slate-700">
              <strong>Su posición actual:</strong> ÉTICO <strong>{v.x_etico}</strong> · ISO <strong>{v.y_iso}</strong> · NIST <strong>{v.z_nist}</strong> sobre 100.
              {' '}
              {score < 40 && 'Su organización está en zona de riesgo — conviene priorizar las brechas altas.'}
              {score >= 40 && score <= 70 && 'Su organización tiene una base, pero hay brechas importantes que atender.'}
              {score > 70 && 'Su organización tiene un nivel sólido — mantenga las prácticas y cierre las brechas restantes.'}
            </p>
          </div>
        )}

        {/* Leyenda de plazos */}
        <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-slate-600">
          <span className="font-medium">Plazos de implementación según gravedad:</span>
          <span className="inline-flex items-center gap-1"><Clock className="w-3.5 h-3.5 text-red-500" /> Alta → 0–30 días</span>
          <span className="inline-flex items-center gap-1"><Clock className="w-3.5 h-3.5 text-amber-500" /> Media → 30–90 días</span>
          <span className="inline-flex items-center gap-1"><Clock className="w-3.5 h-3.5 text-emerald-500" /> Baja → 3–6 meses</span>
        </div>
      </section>

      {/* Gráficas: 3D full width + 3 radares en fila */}
      <section className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold">Espacio 3D del diagnóstico</h2>
        <p className="text-xs text-slate-500 mb-3">
          Ejes 0–100 · X=ÉTICO · Y=ISO · Z=NIST. Cubos de referencia en 50 (aceptable) y 80 (óptima). Interactúe para rotar.
        </p>
        {sinDatos ? (
          <div className="flex items-center justify-center h-[500px] rounded-lg bg-slate-50 border border-dashed border-slate-200">
            <p className="text-sm text-slate-500">Sin datos suficientes para representar el vector 3D.</p>
          </div>
        ) : (
          <Plot
            data={traces3d}
            layout={layout3d}
            config={{ displayModeBar: true, responsive: true, scrollZoom: true }}
            useResizeHandler
            style={{ width: '100%', height: '500px' }}
          />
        )}
      </section>

      <div className="grid gap-6 lg:grid-cols-3">
        <section className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold">Radar NIST AI RMF</h2>
          <p className="text-xs text-slate-500 mb-3">Madurez por función (0–100).</p>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={nistData} outerRadius="70%">
              <PolarGrid />
              <PolarAngleAxis dataKey="name" tick={{ fontSize: 11, fill: '#334155' }} />
              <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
              <Radar dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.35} />
            </RadarChart>
          </ResponsiveContainer>
        </section>

        <section className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold">Radar ISO 42001</h2>
          <p className="text-xs text-slate-500 mb-3">Cobertura por área de control (0–100).</p>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={isoData} outerRadius="65%">
              <PolarGrid />
              <PolarAngleAxis dataKey="name" tick={{ fontSize: 9, fill: '#334155' }} />
              <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
              <Radar dataKey="value" stroke="#0ea5e9" fill="#0ea5e9" fillOpacity={0.35} />
            </RadarChart>
          </ResponsiveContainer>
        </section>

        <section className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-lg font-semibold">Radar principios éticos</h2>
          <p className="text-xs text-slate-500 mb-3">UNESCO + OCDE (0–100).</p>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={eticaData} outerRadius="70%">
              <PolarGrid />
              <PolarAngleAxis dataKey="name" tick={{ fontSize: 10, fill: '#334155' }} />
              <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
              <Radar dataKey="value" stroke="#9333ea" fill="#9333ea" fillOpacity={0.35} />
            </RadarChart>
          </ResponsiveContainer>
          {eticaIncompleta && (
            <p className="text-xs text-amber-600 mt-2">* Principio sin datos suficientes (mostrado como 0).</p>
          )}
        </section>
      </div>

      {/* Gap register enriquecido */}
      <section className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-start gap-3 mb-4">
          <ShieldAlert className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <div>
            <h2 className="text-lg font-semibold">Brechas detectadas (gap register)</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              {gaps.length} brechas ordenadas por gravedad. Cada brecha indica el control ISO 42001 afectado, su fuente normativa, y el plazo recomendado de implementación según la severidad.
            </p>
          </div>
        </div>

        {gaps.length === 0 ? (
          <div className="flex items-center gap-2 text-sm text-emerald-600">
            <CheckCircle2 className="w-5 h-5" />
            No se identificaron brechas. Su organización cumple los controles evaluados.
          </div>
        ) : (
          <div className="space-y-3">
            {gaps.map((g) => (
              <div key={g.id_control} className="border border-slate-200 rounded-lg p-4 hover:border-slate-300 transition-colors">
                <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${badgeSev(g.severidad)}`}>
                        {g.severidad}
                      </span>
                      <span className="font-mono text-xs text-slate-500">ISO 42001 · {g.id_control}</span>
                      {g.clausula && <span className="text-xs text-slate-400">cláusula {g.clausula}</span>}
                      <span className="text-xs text-slate-400">·</span>
                      <span className="text-xs text-slate-500">estado: {g.estado}</span>
                    </div>
                    <h3 className="text-sm font-semibold text-slate-800 mt-1.5">{g.nombre}</h3>
                    {g.descripcion && (
                      <p className="text-xs text-slate-500 mt-1 leading-relaxed">{g.descripcion}</p>
                    )}
                  </div>
                  <div className={`inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium ${badgePlazo(g.severidad)}`}>
                    <Clock className="w-3.5 h-3.5" />
                    <span>Implementar en: <strong>{g.plazo}</strong></span>
                  </div>
                </div>

                {/* Fuentes normativas claras */}
                <div className="mt-3 pt-3 border-t border-slate-100 flex flex-wrap gap-x-5 gap-y-2 text-xs">
                  {g.nist && g.nist.length > 0 && (
                    <div className="flex items-start gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-indigo-500 mt-0.5 shrink-0" />
                      <div>
                        <span className="text-slate-400 uppercase tracking-wide text-[10px] block">NIST AI RMF</span>
                        <span className="text-slate-700">{g.nist.map((fn) => `${fn} (${ETIQUETA_NIST[fn] || fn})`).join(', ')}</span>
                      </div>
                    </div>
                  )}
                  <div className="flex items-start gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-blue-500 mt-0.5 shrink-0" />
                    <div>
                      <span className="text-slate-400 uppercase tracking-wide text-[10px] block">ISO/IEC 42001</span>
                      <span className="text-slate-700">Anexo A · {g.id_control} {g.clausula ? `(cláusula ${g.clausula})` : ''}</span>
                    </div>
                  </div>
                  {g.principios && g.principios.length > 0 && (
                    <div className="flex items-start gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 text-purple-500 mt-0.5 shrink-0" />
                      <div>
                        <span className="text-slate-400 uppercase tracking-wide text-[10px] block">Principios éticos</span>
                        <span className="text-slate-700">{g.principios.map((p) => ETIQUETA_PRINCIPIO[p] || p).join(' · ')}</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
