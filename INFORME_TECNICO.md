# Informe Técnico — Diagnóstico y RAG

> **Playbook de IA Responsable para PYMES** · Global South AI Safety Hackathon 2026
> Fecha: 2026-06-21 · Anexo técnico del paper

---

## 1. Visión general

El sistema es un SaaS de autodiagnóstico de gobernanza de IA para PYMES que evalúa el uso de IA frente a marcos operativos internacionales (NIST AI RMF, ISO 42001) y un marco ético consolidado (UNESCO + OCDE, Floridi & Cowls 2019). La arquitectura separa estrictamente lo **determinista** (motor de reglas) de lo **generativo** (RAG con LLM), siguiendo el principio rector: **el motor decide, el LLM redacta**.

El sistema entrega tres capas:

| Capa | Qué produce | Naturaleza | Verificabilidad |
|------|-------------|-----------|-----------------|
| **Capa 1 — Diagnóstico** | Perfil, inventario, madurez NIST, brechas ISO, vector 3D | Determinista (reglas) | Reproducible, auditable |
| **Capa 2 — Recomendaciones** | Hoja de ruta priorizada con justificación normativa | Determinista (lookup + aritmética) | Reproducible |
| **Capa 3 — Ejecución (RAG)** | Política de IA generada a la medida, fundamentada en fuentes | Generativa (LLM + retrieval) | Citas validadas + faithfulness |

---

## 2. Diagnóstico — Capa 1

### 2.1 Motor determinista data-driven

El diagnóstico es 100% data-driven: el motor (`engine.py`) no conoce IDs de pregunta concretos ni asume un vocabulario de respuesta fijo. Las preguntas se cargan desde `questions.json` siguiendo un contrato documentado (`data/SCHEMA_PREGUNTAS.md`), y el sistema funciona sin tocar código al reemplazar el árbol.

**Arbol de preguntas cargado:** 15 preguntas base + 19 subpreguntas anidadas = **34 preguntas** (desde `ARBOL_PREGUNTAS.md`, con aprobación humana). Las subpreguntas aparecen condicionalmente según la respuesta del padre.

### 2.2 Tipos de respuesta soportados

El motor maneja seis tipos de pregunta, todos con valores fijos por opción:

| Tipo | Uso | Scoring |
|------|-----|---------|
| `multiple` | Opción única con valores fijos (modelo principal) | `puntaje opción / max opciones` |
| `multiple_seleccion` | Selección múltiple | promedia seleccionados, normaliza |
| `likert` | Escala 1-N (subtipo de multiple) | como `multiple` |
| `numero` | Respuesta numérica con tramos | discretiza por `hasta` → puntaje del tramo |
| `matriz` | Una entrada por sistema (tabla) | agrega (`peor` o `promedio`) |
| `texto` | Texto abierto (justificaciones) | no puntúa; se guarda para el RAG |

**Normalización:** los valores fijos pueden estar en cualquier escala (0/1, 0–3, pesos). El motor normaliza dividiendo por el valor máximo de cada pregunta, así una opción con `puntaje: 2` sobre un máximo de `3` da `0.67` de madurez. Las opciones con `puntaje: null` ("No aplica") no entran en los promedios.

### 2.3 Mapeo y ejes del diagnóstico

Cada pregunta lleva un `mapeo` que indica qué control evalúa:

```jsonc
"mapeo": {
  "nist": ["GOVERN", "MEASURE-2.11"],   // función y/o subcategoría
  "iso":  ["A.9.2"],                    // control ISO 42001
  "principio": ["autonomia"]            // principio ético (UNESCO/OCDE)
}
```

Los **tres ejes del diagnóstico** se derivan del mapeo (sin campo `eje` redundante):

| Eje | Dimensión | Cálculo |
|-----|-----------|---------|
| **ÉTICO** (x) | 5 principios consolidados | promedio ponderado de `mapeo.principio` |
| **ISO** (y) | Cobertura ISO 42001 | promedio ponderado de `mapeo.iso` |
| **NIST** (z) | Madurez 4 funciones NIST | promedio ponderado de `mapeo.nist` |

Cada pregunta puede aportar a los tres ejes simultáneamente. Al final del diagnóstico, el motor emite un **vector (x, y, z)**, cada eje 0–100, que ubica a la organización en un espacio 3D.

### 2.4 Vector de diagnóstico — promedio ponderado

El vector se calcula como **promedio ponderado** por eje, normalizado sobre las preguntas efectivamente puntuadas:

```
            Σᵢ aᵢ · wᵢ,eje
eje = 100 · ─────────────       aᵢ = puntaje normalizado de la respuesta i (0..1)
              Σᵢ wᵢ,eje          wᵢ,eje = peso de la pregunta i en ese eje
```

La suma recorre solo las preguntas **efectivamente puntuadas** (aplicables por bifurcación/condición y no respondidas con "na" o `null`). Esto maneja correctamente:
- **Ramas condicionales**: una PYME que responde menos preguntas sigue siendo comparable.
- **Opción "No aplica"**: no entra en el denominador, no infla ni desinfla el score.

### 2.5 Pesos congelados vía RAG

Los pesos `wᵢ,eje` se fijaron en fase de diseño (no en runtime) mediante un script de una sola vez (`propose_weights.py`) que usó el RAG para proponer los 90 pesos (30 preguntas × 3 ejes) con justificación fundamentada en NIST/ISO/principios. El equipo los revisó y congeló en el campo `pesos` de cada pregunta.

**Resultado:** runtime 100% determinista — mismas respuestas → mismas coordenadas para todas las PYMES. El RAG participó solo en diseño, no en cada sesión.

**Verificación de discriminación:**
- Caso PYME fuerte en ético/débil en ISO: **ÉTICO 81 > ISO 77 ≈ NIST 77**
- Caso PYME fuerte en ISO/débil en ético: **ÉTICO 38 < ISO 43 ≈ NIST 45**

Los pesos finos son los que separan las coordenadas y les dan significado (con pesos binarios el vector colapsa a valores uniformes).

### 2.6 Outputs de Capa 1

| Output | Cálculo |
|--------|---------|
| 1.1 Perfil | de la bifurcación inicial (1/2/3) |
| 1.2 Inventario de casos de uso | data-driven vía etiqueta `caso_uso` o tipo `matriz` |
| 1.3 Madurez NIST + subcategorías | promedio de puntajes por función y subcategoría |
| Eje ético por principio | promedio de puntajes por principio (UNESCO/OCDE) |
| 1.4 Cobertura ISO | estado por control (peor estado gana si múltiples preguntas lo tocan) |
| 1.5 Gap register | controles no implementados, ordenados por severidad |
| 1.6 Verificabilidad | % de respuestas con evidencia adjunta (bajo/medio/alto) |
| **Vector (x, y, z)** | promedio ponderado por eje, 0–100 |

### 2.7 Recomendaciones — Capa 2

Determinista por lookup: cada brecha en el gap register se busca en `recommendations.json` (tabla curada brecha → recomendación por control ISO). Una brecha sin control de destino no genera recomendación (cumple `PROPUESTAFINAL §149`).

**Priorización:** `prioridad = severidad / esfuerzo` (mayor = quick win de alto impacto). Cada recomendación incluye justificación normativa (output 2.3) anclada en ISO 42001, NIST AI RMF y los principios éticos UNESCO/OCDE.

---

## 3. RAG — Capa 3

### 3.1 Arquitectura del pipeline

```
Brechas (Capa 2)
      │
      ▼
┌─────────────────────────┐
│  RETRIEVAL HÍBRIDO       │  ← 3 rutas combinadas + RRF + rerank + umbral
│  estructurado + BM25     │
│  + denso (Voyage)        │
└──────────┬──────────────┘
           │ chunks normativos
           ▼
┌─────────────────────────┐
│  GENERACIÓN (LLM)        │  ← OpenCode API (glm-5.2) + prompt grounded-only
│  política a la medida    │
└──────────┬──────────────┘
           │ política + citas
           ▼
┌─────────────────────────┐
│  VERIFICACIÓN            │  ← 2 guardrails: citas + faithfulness
│  (3 capas anti-aluc.)    │
└─────────────────────────┘
```

### 3.2 Retrieval híbrido (3 rutas + RRF + rerank)

El retriever (`rag/retriever.py`) combina tres rutas de búsqueda:

| Ruta | Qué hace | Requiere |
|------|----------|----------|
| **Estructurada** (espinazo) | Filtro por `id_control` / `funcion_nist` que la pregunta ya trae | nada (determinista) |
| **Léxica (BM25)** | Coincidencia de términos (siglas, "Artículo 15", "A.7.2") | `rank-bm25` |
| **Densa (Voyage)** | Embeddings semánticos (lenguaje llano ↔ jerga legal, español ↔ inglés) | `VOYAGE_API_KEY` |

**Fusión RRF (Reciprocal Rank Fusion):** combina los rankings de BM25 + denso por `score = Σ 1/(k + rank)`, con `k=60`. El espinazo estructurado recibe un boost fuerte (chunk que casa por ID/función suma +1.0 al fused score).

**Reranking:** el top-k fusionado se reordena con un cross-encoder (Voyage `rerank-2`) que mira query+chunk juntos → gran salto de precisión.

**Umbral de abstención:** si ningún chunk supera `RETRIEVAL_THRESHOLD=0.35` tras el rerank, el sistema **se abstiene** en vez de generar ("sin fundamento normativo suficiente"). Esto materializa el indicador de verificabilidad y previene el "cumplimiento cosmético".

**Degradación con elegancia:** sin `VOYAGE_API_KEY` degrada a estructurado + BM25 (RAG real, sin dependencia de red). Sin `OPENCODE_API_KEY` la política sale de plantilla. La demo nunca depende de la red.

**Optimización:** los embeddings del corpus se calculan una sola vez y se cachean en disco (`data/cache/embeddings.json`, 29 chunks, 658 KB). Las consultas siguientes solo embeben la query (~1s).

### 3.3 Generación con LLM

El generador (`rag/generator.py`) usa la **API de OpenCode Go** (OpenAI-compatible):

- **Endpoint:** `https://opencode.ai/zen/go/v1/chat/completions`
- **Modelo:** `glm-5.2` (modelo de razonamiento, ~30s por política)
- **Autenticación:** key de `~/.local/share/opencode/auth.json` (opencode-go), sin key de Anthropic separada
- **Cliente:** `rag/llm_client.py` (delgado, sin SDK pesado)

**Prompt grounded-only:** el sistema instruye al modelo a basarse ÚNICAMENTE en los documentos normativos proporcionados, citar la `referencia_legal` de cada obligación, y no inventar lo que no esté en las fuentes. Las fuentes se inyectan en el prompt con su texto y referencia.

**Limpieza de preamble:** glm-5.2 es un modelo de razonamiento que a veces emite su cadena de razonamiento visible antes de la respuesta. Un limpiador (`_limpiar_salida`) detecta y remueve el preamble, conservando solo la política final.

**Modelo híbrido (configuración):**
- `OPENCODE_MODEL=glm-5.2` para generación de política (razonamiento, calidad)
- `OPENCODE_MODEL_JSON=deepseek-v4-flash` para tareas JSON estructuradas (configurado, uso futuro)

### 3.4 Las tres capas de defensa anti-alucinación

Inspiradas en el modelo de "queso suizo" de Hendrycks — los huecos de una capa los tapa la siguiente:

#### Capa 1 — Retrieval con umbral de abstención
Si ningún chunk supera el umbral (0.35) tras el rerank, el sistema no genera. **Resultado en el golden set: 0 abstenciones** (las 10 consultas tuvieron fundamento suficiente).

#### Capa 2 — Validación determinista de citas (`rag/verifier.py`)
Toda referencia normativa que el LLM mencione (controles ISO, funciones NIST) debe existir realmente en el corpus o en `controls.json`. Si el modelo inventa "ISO 42001 A.99" o "NIST AI RMF 9.9" inexistente, se detecta automáticamente.

**Mecanismo:** regex que extrae citas del texto (`art. N`, `A.N.N`, `ley 1581`, `conpes 4144`), las normaliza, y verifica contra un índice construido del corpus + `controls.json`. Barato, determinista, sin LLM.

**Resultado:** **precisión de citas = 1.0** (100% — cero citas inválidas en las 10 políticas del golden set).

#### Capa 3 — Verificador de faithfulness (`rag/faithfulness.py`, LLM-as-judge)
Una segunda llamada LLM comprueba que cada afirmación atómica de la política está **entailed** por las fuentes citadas (groundedness, métrica de faithfulness de RAGAS aplicada en línea).

**Flujo:**
1. El LLM recibe la política + las fuentes.
2. Identifica cada afirmación atómica.
3. Para cada una: veredicto `faithful` | `unfaithful` | `partial`, con fuente citada y explicación.
4. Agrega: `score = faithful / total`, lista de no respaldadas.

**Criterios del prompt:**
- `faithful` = contenido sustantivo entailed en alguna fuente (paráfrasis fiel vale)
- `unfaithful` = introduce obligaciones, artículos o detalles no presentes en las fuentes (inventados)
- `partial` = parte respaldada, parte no

**Modelo:** `glm-5.2` (fiable para JSON estructurado; verificado con `propose_weights.py`). Una sola llamada LLM por política (eficiente). Extractor de JSON robusto con escaneo de llaves balanceadas para manejar razonamiento-before-JSON.

**Resultado:** **faithfulness media = 0.884** (min 0.684, max 1.0, n=10). 13 afirmaciones no respaldadas detectadas en total.

**Esta es la salvaguarda de seguridad de IA más diferenciadora del proyecto** — técnicamente es una salvaguarda de faithfulness en línea, alineada con el tema del hackathon.

---

## 4. Evaluación RAGAS — métricas para el paper

### 4.1 Golden set

> Pendiente de regeneración con el corpus normativo universal (NIST AI RMF, ISO 42001 y principios éticos UNESCO/OCDE).

El golden set original cubría 10 consultas representativas del árbol (supervisión humana, datos personales, gobernanza de datos, política de IA, roles, evaluación de impacto, transparencia, IA de terceros, incidentes, beneficencia). Al migrar a un corpus exclusivamente universal, se eliminó el golden set anterior y se dejará un nuevo conjunto de consultas-oro con referencias esperadas de ISO/NIST/principios.

### 4.2 Harness de evaluación (`eval_harness.py`)

Paralelizado con `ThreadPoolExecutor` (10 workers). Genera una política por consulta + verifica faithfulness. Modelos: `glm-5.2` para política y faithfulness (fiable para JSON).

### 4.3 Métricas finales

> Por regenerar tras la migración al corpus universal.

| Métrica | Definición | Resultado |
|---------|-----------|-----------|
| **Recall@6** | % de fuentes esperadas que aparecen en el top-6 recuperado | Pendiente |
| **Precisión de citas** | % de citas en la política que existen en el corpus | Pendiente |
| **Faithfulness** | % de afirmaciones respaldadas por las fuentes (LLM-as-judge) | Pendiente |
| **Abstenciones** | Consultas sin fundamento suficiente | Pendiente |

---

## 5. Stack técnico

| Componente | Tecnología | Archivo |
|-----------|-----------|---------|
| Motor determinista | Python 3.14, funciones puras | `engine.py` |
| API | FastAPI + uvicorn | `main.py` |
| Retrieval léxico | rank-bm25 | `rag/retriever.py` |
| Retrieval semántico | Voyage AI (`voyage-3` + `rerank-2`) | `rag/retriever.py` |
| Generación LLM | OpenCode Go API (`glm-5.2`) | `rag/llm_client.py`, `rag/generator.py` |
| Verificador de citas | regex + índice del corpus | `rag/verifier.py` |
| Verificador de faithfulness | LLM-as-judge (`glm-5.2`) | `rag/faithfulness.py` |
| Pesos vía RAG | OpenCode Go API (`glm-5.2`) | `propose_weights.py` |
| Evaluación RAGAS | ThreadPoolExecutor + métricas | `eval_harness.py` |
| Datos | JSON (preguntas, controles, corpus, recomendaciones) | `data/` |

**Sin dependencias pesadas:** no hay Qdrant/ChromaDB (los embeddings se cachean en JSON), no hay Anthropic SDK (cliente HTTP delgado), no hay base de datos (estado solo en sesión).

---

## 6. Archivos clave

```
app/backend/
├── engine.py                 # motor determinista (Capa 1 + 2)
├── main.py                   # API FastAPI
├── propose_weights.py        # pesos congelados vía RAG (una sola vez)
├── validate_questions.py     # validador del árbol
├── eval_harness.py           # harness RAGAS (recall, citas, faithfulness)
├── poc.py                    # caso de prueba end-to-end
├── rag/
│   ├── llm_client.py         # cliente OpenCode API
│   ├── retriever.py          # retrieval híbrido (estructurado + BM25 + Voyage + RRF + rerank)
│   ├── generator.py          # generación de política (Capa 3)
│   ├── verifier.py           # validación de citas (2ª capa anti-alucinación)
│   └── faithfulness.py       # verificador LLM-as-judge (3ª capa anti-alucinación)
└── data/
    ├── questions.json        # árbol (15 base + 19 subpreguntas, pesos congelados)
    ├── controls.json         # controles ISO 42001 + principios éticos
    ├── recommendations.json  # lookup brecha → recomendación
    ├── corpus/               # chunks normativos con metadatos
    ├── golden_set.json       # 10 consultas-oro para evaluación
    ├── eval_result.json      # resultados del harness
    ├── eval_report.md        # reporte markdown
    ├── pesos_propuestos.json # pesos propuestos por el RAG (congelados en questions.json)
    └── SCHEMA_PREGUNTAS.md   # contrato del árbol
```

---

## 7. Decisiones de diseño (no relitigar)

1. **Fuente de verdad:** `PROPUESTAFINAL.md` + `ARBOL_PREGUNTAS.md` (aprobación humana). El sistema se adaptó al árbol, no al revés.
2. **Marco ético:** 5 principios consolidados (Beneficencia, No maleficencia, Autonomía, Justicia, Explicabilidad) desde UNESCO + OCDE (Florili & Cowls 2019). Corpus normativo universal: NIST AI RMF, ISO 42001 y principios éticos consolidados.
3. **Ejes del diagnóstico:** ÉTICO, NIST, ISO (se eliminaron LEGAL y RESPONSABILIDAD como ejes; la dimensión legal/estatutaria se deja para futuros paquetes país). Se derivan del `mapeo`, sin campo `eje`.
4. **Diagnóstico visual:** vector (x=ÉTICO, y=ISO, z=NIST) en espacio 3D.
5. **Scoring:** promedio ponderado por eje, normalizado sobre preguntas efectivamente puntuadas.
6. **Pesos:** congelados vía RAG en diseño, no en runtime. Runtime determinista.
7. **Principio rector:** el motor decide, el RAG redacta. La lógica con consecuencia legal es determinista y auditable.
8. **LLM vía OpenCode (no Anthropic):** API de OpenCode Go, key de auth.json. Sin key de Anthropic separada.
9. **Evidencia documental:** voluntaria (coherente con §6.3 de PROPUESTAFINAL).
10. **Modo degradado:** todo corre sin keys para que la demo nunca dependa de la red.

---

## 8. Verificación final (2026-06-21)

- ✅ Validador: el árbol cumple el contrato
- ✅ POC end-to-end: vector discrimina (25/27/28 en caso débil; 81/77/77 en caso fuerte ético)
- ✅ API: `modo: completo`, `llm: True`, `voyage: True`
- ✅ Política generada con LLM: 4316 chars, 6 citas, verificación ok=True
- ✅ Faithfulness integrado en `/policy` (`faithfulness=true`)
- ⏳ Harness RAGAS: pendiente de regeneración con corpus normativo universal

**El diagnóstico y el RAG están completos para el paper y la demo. Las métricas RAGAS se actualizarán en la siguiente versión del paper.**
