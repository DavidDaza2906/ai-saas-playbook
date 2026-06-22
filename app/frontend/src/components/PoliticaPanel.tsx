import type { ReactNode } from 'react'
import { FileText, Download, BookOpen, CheckCircle2, AlertTriangle } from 'lucide-react'
import type { PolicyResponse } from '../types'

const CITA_RE =
  /(ISO\s+42001(?:\s+A\.\d+(?:\.\d+)*)?|NIST\s+AI\s+RMF(?:\s+\d+\.\d+)?|\bGOVERN\b|\bMAP\b|\bMEASURE\b|\bMANAGE\b)/gi

function resaltarCitas(texto: string): ReactNode[] {
  const nodos: ReactNode[] = []
  let ultimo = 0
  let i = 0
  for (const m of texto.matchAll(CITA_RE)) {
    const inicio = m.index ?? 0
    if (inicio > ultimo) nodos.push(texto.slice(ultimo, inicio))
    nodos.push(
      <mark key={`c-${i++}`} className="bg-yellow-200 rounded px-0.5">
        {m[0]}
      </mark>
    )
    ultimo = inicio + m[0].length
  }
  if (ultimo < texto.length) nodos.push(texto.slice(ultimo))
  return nodos
}

function descargarMarkdown(texto: string) {
  const blob = new Blob([texto], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'politica-ia.md'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

export function PoliticaPanel({
  policy,
  cargando,
  onGenerar,
}: {
  policy: PolicyResponse | null
  cargando: boolean
  onGenerar: () => void
}) {
  if (cargando) {
    return (
      <div className="bg-white rounded-xl border p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center shrink-0">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
          </div>
          <div>
            <h2 className="text-lg font-semibold">Generando política con RAG…</h2>
            <p className="text-sm text-slate-600">Esto toma ~1-2 min.</p>
          </div>
        </div>
        <div className="space-y-3">
          <div className="h-3 bg-slate-100 rounded animate-pulse"></div>
          <div className="h-3 bg-slate-100 rounded animate-pulse w-5/6"></div>
          <div className="h-3 bg-slate-100 rounded animate-pulse w-4/6"></div>
        </div>
      </div>
    )
  }

  if (policy === null) {
    return (
      <div className="bg-white rounded-xl border p-6">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center shrink-0">
            <FileText className="w-5 h-5 text-indigo-600" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-semibold">Política de IA a la medida</h2>
            <p className="text-sm text-slate-600 mt-1">
              Genere una política de uso responsable de IA fundamentada en las fuentes
              normativas aplicables a su organización. La política es descargable y
              puede adoptarse como guía interna.
            </p>
            <button
              onClick={onGenerar}
              className="mt-5 inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
            >
              <BookOpen className="w-4 h-4" /> Generar política
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (policy.abstain) {
    return (
      <div className="bg-white rounded-xl border p-6">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center shrink-0">
            <AlertTriangle className="w-5 h-5 text-amber-600" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-semibold">Sin fundamento normativo suficiente</h2>
            <p className="text-sm text-slate-600 mt-1">
              El sistema no encontró fuentes suficientes para generar una política fundamentada.
              Es preferible abstenerse antes que generar contenido sin respaldo normativo.
            </p>
            {policy.mensaje && (
              <p className="text-sm text-slate-500 mt-2 italic bg-slate-50 rounded p-2">
                {policy.mensaje}
              </p>
            )}
            <button
              onClick={onGenerar}
              className="mt-4 inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
            >
              <BookOpen className="w-4 h-4" /> Reintentar
            </button>
          </div>
        </div>
      </div>
    )
  }

  const p = policy.politica
  if (!p) {
    return (
      <div className="bg-white rounded-xl border p-6">
        <p className="text-sm text-slate-600">No hay política disponible.</p>
        <button
          onClick={onGenerar}
          className="mt-3 inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
        >
          <BookOpen className="w-4 h-4" /> Generar política
        </button>
      </div>
    )
  }

  const fuentes = policy.fuentes ?? []
  const verif = policy.verificacion

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="bg-white rounded-xl border p-6">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <FileText className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-semibold">Política de uso responsable de IA</h2>
            {p.modo === 'llm' ? (
              <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
                Generada a la medida
              </span>
            ) : (
              <span className="text-xs px-2 py-1 rounded-full bg-amber-100 text-amber-700">
                Plantilla base
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-500">{p.texto.length} caracteres</span>
            <button
              onClick={() => descargarMarkdown(p.texto)}
              className="inline-flex items-center gap-1.5 text-sm border rounded-lg px-3 py-1.5 hover:bg-slate-50 transition-colors"
            >
              <Download className="w-4 h-4" /> Descargar .md
            </button>
          </div>
        </div>

        {/* Sello de confianza simple (sin detalles técnicos) */}
        {verif?.ok && (
          <div className="mt-4 flex items-center gap-2 text-sm text-green-700 bg-green-50 rounded-lg p-3">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>Política verificada — todas las citas son válidas frente a las fuentes normativas.</span>
          </div>
        )}
        {verif && !verif.ok && (
          <div className="mt-4 flex items-center gap-2 text-sm text-amber-700 bg-amber-50 rounded-lg p-3">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span>La política contiene {verif.invalidas.length} cita(s) que no se reconocen en las fuentes. Revise antes de adoptarla.</span>
          </div>
        )}
      </div>

      {/* Texto de la política */}
      <div className="bg-white rounded-xl border p-6">
        <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
          <FileText className="w-4 h-4 text-slate-500" /> Texto de la política
        </h3>
        {p.error && (
          <div className="mb-3 flex items-start gap-2 text-sm text-red-700 bg-red-50 rounded-lg p-3">
            <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
            <span>{p.error}</span>
          </div>
        )}
        <div className="whitespace-pre-wrap text-sm leading-relaxed text-slate-800 bg-slate-50 rounded-lg p-4 font-serif">
          {resaltarCitas(p.texto)}
        </div>
        {p.citas.length > 0 && (
          <p className="text-xs text-slate-500 mt-3">
            {p.citas.length} cita(s) en el texto · referencias resaltadas en amarillo
          </p>
        )}
      </div>

      {/* Fuentes normativas (simples, sin scores técnicos) */}
      {fuentes.length > 0 && (
        <div className="bg-white rounded-xl border p-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-slate-500" /> Fuentes normativas en las que se basa
          </h3>
          <ul className="space-y-2">
            {fuentes.map((f, idx) => (
              <li key={idx} className="py-2 border-b last:border-b-0 border-slate-100">
                <div className="text-sm font-semibold text-slate-800">{f.referencia}</div>
                <div className="text-xs text-slate-500">{f.fuente}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
