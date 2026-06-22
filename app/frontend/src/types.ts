// Tipos TypeScript del diagnóstico — espejo del backend (engine.py + main.py).

export type ValorRespuesta = string | string[] | number

export interface Opcion {
  valor: string
  etiqueta: string
  puntaje?: number | null
}

export interface Subpregunta {
  id: string
  texto: string
  contexto_pyme: string
  tipo: string
  opciones?: Opcion[]
  tramos?: { hasta: number | null; etiqueta: string; puntaje: number | null; valor_tramo: string }[]
  condicion?: { pregunta: string; en: string[]; modo?: string }
  ramas?: string[]
  mapeo: Mapeo
  subpreguntas?: Subpregunta[]
}

export interface Pregunta extends Omit<Subpregunta, 'condicion'> {
  condicion?: { pregunta: string; en: string[]; modo?: string }
  caso_uso?: { caso: string; riesgo: string; cuando: string[] }
  filas_de?: string
  agregacion?: string
}

export interface Mapeo {
  nist?: string[]
  iso?: string[]
  principio?: string[]
}

export interface Bifurcacion {
  id: string
  texto: string
  contexto_pyme: string
  tipo: string
  opciones: Opcion[]
}

export interface ArbolPreguntas {
  bifurcacion: Bifurcacion
  preguntas: Pregunta[]
  estado_opciones: Opcion[]
}

export interface VectorDiagnostico {
  x_etico: number | null
  y_iso: number | null
  z_nist: number | null
}

export interface Gap {
  id_control: string
  nombre: string
  descripcion?: string
  clausula?: string
  estado: string
  severidad: 'alta' | 'media' | 'baja'
  plazo?: string
  ejes: string[]
  nist?: string[]
  principios: string[]
}

export interface Recomendacion {
  id_control: string
  brecha: string
  recomendacion: string
  nist: string
  esfuerzo: 'bajo' | 'medio' | 'alto'
  fase: '0-30' | '30-90' | 'estructural'
  rol: string
  criterio_cierre: string
  severidad: string
  ejes: string[]
  principios: string[]
  prioridad: number
  plano: { x_esfuerzo: number; y_riesgo: number }
  justificacion: {
    fundamento_constitucional: string[]
    principios_eticos: string[]
    control_iso: string
    funcion_nist: string
  }
}

export interface Diagnostico {
  perfil: { bifurcacion: string; descripcion: string }
  inventario: { caso: string; riesgo: string }[]
  diagnostico_vector: VectorDiagnostico
  madurez_nist: Record<string, number | null>
  subcategorias_nist: Record<string, number | null>
  principios_eticos: Record<string, number | null>
  cobertura_iso: { id_control: string; nombre: string; clausula: string; estado: string; puntaje: number }[]
  gap_register: Gap[]
  verificabilidad: {
    respondidas: number
    con_evidencia: number
    nivel: string
    detalle: Record<string, string>
  }
  texto_abierto: Record<string, string>
}

export interface DiagnoseResponse {
  capa1: Diagnostico
  capa2: Recomendacion[]
}

export interface FuenteRecuperada {
  fuente: string
  referencia: string
  score?: number
}

export interface FaithfulnessResult {
  modo: 'llm' | 'heuristica'
  claims: { afirmacion: string; veredicto: 'faithful' | 'unfaithful' | 'partial'; fuente_citada: string | null; explicacion: string }[]
  n_claims: number
  n_faithful: number | null
  n_unfaithful: number | null
  n_partial: number
  score: number | null
  faithful: boolean
  no_respaldadas: { afirmacion: string; veredicto: string; fuente_citada: string | null; explicacion: string }[]
  error?: string
}

export interface PolicyResponse {
  abstain: boolean
  mensaje?: string
  politica?: { texto: string; citas: { fuente: string }[]; modo: 'llm' | 'plantilla'; error?: string }
  fuentes?: FuenteRecuperada[]
  verificacion?: { validas: string[]; invalidas: string[]; ok: boolean }
  faithfulness?: FaithfulnessResult | null
}

export interface TareaPlan {
  control: string
  brecha: string
  accion: string
  responsable: string
  fase: string
  criterio_cierre: string
  prioridad: number
  esfuerzo: string
  severidad: string
}

export interface PlanAccionable {
  fases: Record<string, TareaPlan[]>
  resumen: { n_tareas: number; n_quick_wins_0_30: number; n_mediano_plazo_30_90: number; n_estructural: number }
}

export interface Constancia {
  titulo: string
  fecha_evaluacion: string
  organizacion: { perfil: string | null; pais: string | null; sector: string | null }
  que_se_evaluo: { preguntas_respondidas: number; con_evidencia: number; bifurcacion: string }
  que_se_encontro: {
    vector_diagnostico: VectorDiagnostico
    madurez_nist: Record<string, number | null>
    principios_eticos: Record<string, number | null>
    brechas_por_severidad: Record<string, number>
    n_brechas_total: number
    nivel_verificabilidad: string
  }
  que_se_genero: {
    recomendaciones: number
    plan_accionable: { n_tareas: number; n_quick_wins_0_30: number; n_mediano_plazo_30_90: number; n_estructural: number }
    politica_generada: boolean
    politica_modo: string | null
    politica_citas: number
  }
  marco_normativo: { nist_ai_rmf: string; iso_42001: string; principios_eticos: string }
  disclaimer: string
}

export interface ArtifactsResponse {
  plan: PlanAccionable
  plan_markdown: string
  constancia: Constancia
  constancia_markdown: string
}
