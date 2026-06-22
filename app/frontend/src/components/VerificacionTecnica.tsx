import {
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  BookOpen,
  ChevronDown,
  XCircle,
} from 'lucide-react'
import type { PolicyResponse, FaithfulnessResult } from '../types'

function badgeScore(score?: number): { texto: string; cls: string } {
  if (score === undefined) return { texto: '—', cls: 'bg-slate-100 text-slate-600' }
  if (score >= 1.0) return { texto: 'estructurado', cls: 'bg-blue-100 text-blue-700' }
  if (score >= 0.6) return { texto: 'rerank', cls: 'bg-purple-100 text-purple-700' }
  if (score >= 0.3) return { texto: 'densa', cls: 'bg-indigo-100 text-indigo-700' }
  return { texto: 'BM25', cls: 'bg-slate-200 text-slate-700' }
}

function colorScore(score: number): string {
  if (score > 0.9) return 'text-green-600'
  if (score >= 0.7) return 'text-amber-600'
  return 'text-red-600'
}

function barraScore(score: number): string {
  if (score > 0.9) return 'bg-green-500'
  if (score >= 0.7) return 'bg-amber-500'
  return 'bg-red-500'
}

function badgeVeredicto(v: string): { texto: string; cls: string } {
  if (v === 'faithful') return { texto: '✓ Faithful', cls: 'bg-green-100 text-green-700' }
  if (v === 'unfaithful') return { texto: '✗ Unfaithful', cls: 'bg-red-100 text-red-700' }
  return { texto: '⚠ Partial', cls: 'bg-amber-100 text-amber-700' }
}

function FaithfulnessBloque({ f }: { f: FaithfulnessResult }) {
  if (f.error) {
    return (
      <div className="flex items-start gap-2 text-sm text-red-700 bg-red-50 rounded-lg p-3">
        <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
        <span>Error en verificador de faithfulness: {f.error}</span>
      </div>
    )
  }

  if (f.modo === 'heuristica') {
    return (
      <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-amber-100 text-amber-700">
        <AlertTriangle className="w-3.5 h-3.5" /> Modo heurística (sin LLM)
      </span>
    )
  }

  const score = f.score ?? 0
  const nNoRespaldadas = (f.n_unfaithful ?? 0) + f.n_partial

  return (
    <div className="space-y-4">
      <div className="flex items-end gap-4 flex-wrap">
        <div>
          <div className={`text-3xl font-bold ${colorScore(score)}`}>
            {Math.round(score * 100)}%
          </div>
          <div className="text-xs text-slate-500">faithfulness</div>
        </div>
        <div className="flex-1 min-w-[180px]">
          <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className={`h-full ${barraScore(score)} transition-all`}
              style={{ width: `${Math.round(score * 100)}%` }}
            />
          </div>
        </div>
        {f.faithful ? (
          <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
            <CheckCircle2 className="w-3.5 h-3.5" /> ✓ Política respaldada
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-amber-100 text-amber-700">
            <AlertTriangle className="w-3.5 h-3.5" /> ⚠ {nNoRespaldadas} afirmaciones no respaldadas
          </span>
        )}
      </div>

      <p className="text-sm text-slate-600">
        {f.n_claims} afirmaciones ·{' '}
        <span className="text-green-700 font-medium">{f.n_faithful ?? 0} faithful</span> ·{' '}
        <span className="text-red-700 font-medium">{f.n_unfaithful ?? 0} unfaithful</span> ·{' '}
        <span className="text-amber-700 font-medium">{f.n_partial} partial</span>
      </p>

      {f.no_respaldadas.length > 0 && (
        <details className="group">
          <summary className="cursor-pointer flex items-center gap-2 text-sm font-medium text-slate-700 hover:text-slate-900">
            <ChevronDown className="w-4 h-4 group-open:rotate-180 transition-transform" />
            {f.no_respaldadas.length} afirmación(es) no respaldadas (detalle del LLM-as-judge)
          </summary>
          <ul className="mt-3 space-y-3 pl-1">
            {f.no_respaldadas.map((c, idx) => {
              const b = badgeVeredicto(c.veredicto)
              return (
                <li key={idx} className="border-l-2 border-slate-200 pl-3 py-1">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${b.cls}`}>{b.texto}</span>
                    {c.fuente_citada && (
                      <span className="text-xs text-slate-500">cita: {c.fuente_citada}</span>
                    )}
                  </div>
                  <p className="text-sm text-slate-800">{c.afirmacion}</p>
                  {c.explicacion && (
                    <p className="text-xs text-slate-500 italic mt-1">→ {c.explicacion}</p>
                  )}
                </li>
              )
            })}
          </ul>
        </details>
      )}
    </div>
  )
}

function CapaBadge({ n, texto, ok, ejecutada }: { n: number; texto: string; ok: boolean; ejecutada: boolean }) {
  if (!ejecutada) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-slate-100 text-slate-500">
        <span className="w-4 h-4 rounded-full bg-slate-300 text-white flex items-center justify-center text-[10px] font-bold">
          {n}
        </span>
        {texto}
        <span className="text-slate-400">· omitida</span>
      </span>
    )
  }
  if (ok) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-green-50 text-green-700 border border-green-200">
        <CheckCircle2 className="w-3.5 h-3.5" />
        <span className="font-medium">{n}. {texto}</span>
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200">
      <AlertTriangle className="w-3.5 h-3.5" />
      <span className="font-medium">{n}. {texto}</span>
    </span>
  )
}

export function VerificacionTecnica({ policy }: { policy: PolicyResponse | null }) {
  if (!policy || policy.abstain || !policy.politica) {
    return (
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-lg font-semibold mb-2">Verificación técnica</h2>
        <p className="text-sm text-slate-600">
          Genere la política en la pestaña "Política" para ver aquí la verificación técnica
          (citas validadas, faithfulness LLM-as-judge y las 3 capas anti-alucinación).
        </p>
      </div>
    )
  }

  const fuentes = policy.fuentes ?? []
  const verif = policy.verificacion
  const faith = policy.faithfulness

  const capa1Ok = !policy.abstain && fuentes.length > 0
  const capa2Ok = verif?.ok ?? false
  const capa3Ok = faith?.faithful ?? false
  const capa3Ejecutada = faith !== null && faith !== undefined && !faith?.error

  return (
    <div className="space-y-5">
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-lg font-semibold mb-4">Verificación técnica del RAG</h2>
        <p className="text-sm text-slate-600 mb-4">
          Métricas de las 3 capas anti-alucinación (modelo queso suizo de Hendrycks) —
          datos para el paper y validación técnica, no para la empresa.
        </p>
        <div className="flex items-center gap-2 flex-wrap text-xs">
          <CapaBadge n={1} texto="Retrieval + umbral" ok={capa1Ok} ejecutada />
          <span className="text-slate-300">→</span>
          <CapaBadge n={2} texto="Citas validadas" ok={capa2Ok} ejecutada={verif !== undefined} />
          <span className="text-slate-300">→</span>
          <CapaBadge n={3} texto="Faithfulness LLM-as-judge" ok={capa3Ok} ejecutada={capa3Ejecutada} />
        </div>
      </div>

      {fuentes.length > 0 && (
        <div className="bg-white rounded-xl border p-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-1 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-slate-500" /> Fuentes normativas recuperadas
          </h3>
          <p className="text-xs text-slate-500 mb-4">(retrieval híbrido: BM25 + densa + rerank)</p>
          <ul className="space-y-2">
            {fuentes.map((f, idx) => {
              const b = badgeScore(f.score)
              return (
                <li key={idx} className="flex items-start justify-between gap-3 py-2 border-b last:border-b-0 border-slate-100">
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-slate-800">{f.referencia}</div>
                    <div className="text-xs text-slate-500 truncate">{f.fuente}</div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    {f.score !== undefined && (
                      <span className="text-xs text-slate-600 tabular-nums">{Math.round(f.score * 100)}%</span>
                    )}
                    <span className={`text-xs px-2 py-1 rounded-full ${b.cls}`}>{b.texto}</span>
                  </div>
                </li>
              )
            })}
          </ul>
        </div>
      )}

      {verif && (
        <div className="bg-white rounded-xl border p-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-slate-500" /> Verificación de citas (determinista)
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            2ª capa anti-alucinación: cada cita en la política debe existir en las fuentes recuperadas.
          </p>
          {verif.ok ? (
            <div className="flex items-center gap-2 text-sm">
              <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">
                <CheckCircle2 className="w-3.5 h-3.5" /> ✓ Todas las citas son válidas
              </span>
              <span className="text-xs text-slate-500">({verif.validas.length} válidas)</span>
            </div>
          ) : (
            <div className="space-y-2">
              <span className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-red-100 text-red-700">
                <XCircle className="w-3.5 h-3.5" /> ✗ {verif.invalidas.length} cita(s) inválida(s)
              </span>
              <ul className="text-xs text-red-700 list-disc list-inside space-y-0.5">
                {verif.invalidas.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            </div>
          )}
          {verif.validas.length > 0 && (
            <details className="group mt-3">
              <summary className="cursor-pointer text-xs text-slate-500 hover:text-slate-700 flex items-center gap-1">
                <ChevronDown className="w-3.5 h-3.5 group-open:rotate-180 transition-transform" />
                Ver {verif.validas.length} cita(s) válidas
              </summary>
              <ul className="mt-2 text-xs text-slate-400 list-disc list-inside space-y-0.5">
                {verif.validas.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            </details>
          )}
        </div>
      )}

      <div className="bg-white rounded-xl border p-6">
        <h3 className="text-sm font-semibold text-slate-700 mb-1 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-slate-500" /> Faithfulness (LLM-as-judge)
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          3ª capa anti-alucinación: el LLM verifica que cada afirmación de la política esté respaldada por las fuentes.
        </p>
        {faith === null || faith === undefined ? (
          <p className="text-sm text-slate-500 bg-slate-50 rounded-lg p-3">
            No se ejecutó el verificador de faithfulness.
          </p>
        ) : (
          <FaithfulnessBloque f={faith} />
        )}
      </div>
    </div>
  )
}
