// Cliente API — llama al backend FastAPI en /api (proxy Vite a localhost:8000).

import type {
  ArbolPreguntas, DiagnoseResponse, PolicyResponse, ArtifactsResponse, ValorRespuesta,
} from './types'

const BASE = '/api'

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error(`${path} HTTP ${r.status}: ${await r.text()}`)
  return r.json()
}

export async function getQuestions(): Promise<ArbolPreguntas> {
  const r = await fetch(`${BASE}/questions`)
  if (!r.ok) throw new Error(`/questions HTTP ${r.status}`)
  return r.json()
}

export async function getHealth(): Promise<{ ok: boolean; llm: boolean; voyage: boolean; modelo: string; modo: string }> {
  const r = await fetch(`${BASE}/health`)
  return r.json()
}

export interface DiagnosePayload {
  bifurcacion: string
  respuestas: Record<string, ValorRespuesta>
  evidencias?: string[]
  pais?: string | null
  sector?: string | null
}

export async function diagnose(payload: DiagnosePayload): Promise<DiagnoseResponse> {
  return postJson('/diagnose', { ...payload, evidencias: payload.evidencias || [], pais: payload.pais ?? 'CO' })
}

export interface PolicyPayload {
  bifurcacion: string
  sector?: string | null
  pais?: string | null
  brechas: { id_control: string; nombre?: string; brecha?: string; nist?: string }[]
  faithfulness?: boolean
}

export async function generatePolicy(payload: PolicyPayload): Promise<PolicyResponse> {
  return postJson('/policy', { ...payload, faithfulness: payload.faithfulness ?? false, pais: payload.pais ?? 'CO' })
}

export interface ArtifactsPayload extends DiagnosePayload {
  sector?: string | null
  generar_politica?: boolean
  faithfulness?: boolean
}

export async function getArtifacts(payload: ArtifactsPayload): Promise<ArtifactsResponse> {
  return postJson('/artifacts', {
    ...payload,
    evidencias: payload.evidencias || [],
    pais: payload.pais ?? 'CO',
    generar_politica: payload.generar_politica ?? false,
    faithfulness: payload.faithfulness ?? false,
  })
}

// Caso POC precargado para demo rápida (PYME comercio, ruta C, 3 sistemas, uno alto riesgo)
export const CASO_POC: DiagnosePayload = {
  bifurcacion: '3',
  pais: 'CO',
  sector: 'Comercio',
  respuestas: {
    q1: 'parcial', q2: ['c'], q2a: 'parcial',
    q3: 3, q3b: 'algunos', q4: ['medio', 'alto', 'bajo'],
    q5: '2', q5a: 'parcial', q5b: 'no',
    q6: 'si', q6a: 'no', q6b: 'no', q6c: 'no',
    q7: ['c'], q7a: 'nadie', q7b: 'nunca',
    q8a: '2', q8a_just: 'temor a perder clientes',
    q8b: ['d'], q8b_herr: 'no',
    q9b: 'si', q9a: 'no', q9b_doc: 'no',
    q10b: '2', q10a: 'no', q10b_mon: 'nadie',
    q11: 'si', q11a: 'no', q11b: 'no',
    q12: 'si', q12a: 'no', q12b: 'no',
    q13: '3', q13_just: 'creemos que estamos bien pero no sabemos bien qué hacer',
  },
  evidencias: ['q1'],
}
