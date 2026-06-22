# Guía para la Creación de un RAG Confiable
> Versión adaptada al proyecto: SaaS de autodiagnóstico de IA responsable para PYMES (corpus normativo: NIST AI RMF, ISO 42001, Constitución Política de Colombia, CONPES 4144, Ley 1581). Stack: Python + Voyage (embeddings) + Claude Opus 4.8 (generación).

Para construir un sistema RAG (Generación Aumentada por Recuperación) robusto y preciso no basta con conectar un LLM a una base de datos. Se requiere diseño meticuloso en cada etapa del pipeline para evitar alucinaciones y asegurar que las respuestas se basen estrictamente en la información proporcionada.

## 0. Principio rector: determinista vs. generativo
La regla que ordena todo el diseño: **el LLM nunca decide "qué dice la ley"; solo redacta sobre lo que un componente determinista ya recuperó.** La lógica con consecuencia legal (qué control aplica, qué brecha existe, qué fuente la sustenta) es de reglas; el LLM solo aporta lenguaje natural fundamentado. Esta frontera es la mayor palanca de confiabilidad del sistema.

---

## 1. Preparación y Limpieza de Datos (Ingestión)
La calidad del sistema es directamente proporcional a la de los datos (GIGO: Garbage In, Garbage Out).

- **Limpieza profunda:** preparar y limpiar los datos antes de indexarlos suele ser el paso que más tiempo consume en proyectos reales.
- **Extracción de metadatos:** al cargar documentos (PDF, DOCX, etc.) se extraen título, número de página/artículo, autor, categoría. Los metadatos permiten filtrar y restringen el espacio de consulta, mejorando drásticamente la precisión.
- **Metadatos como espinazo determinista (clave en este proyecto):** cada chunk se etiqueta con `fuente`, `id_control` (ej. ISO 42001 A.5), `funcion_nist` (GOVERN/MAP/MEASURE/MANAGE) y `referencia_legal` (ej. art. 15 Constitución, art. 9 Ley 1581). Como cada pregunta del árbol ya viene mapeada a una función NIST / control ISO, gran parte de la recuperación es un **filtro por metadato exacto**, no una búsqueda difusa. Esto es determinista y 100% citable.

## 2. Estrategia de Fragmentación (Chunking)
Indexar documentos completos diluye la señal con ruido.

- **Fragmentos pequeños y semánticos:** 500–2500 caracteres.
- **Splitters inteligentes:** `RecursiveCharacterTextSplitter` u análogos. Prioriza unidades lógicas (párrafo, encabezado, artículo de ley, control) en lugar de cortes arbitrarios.
- **Solapamiento (overlap):** 10%–20% del tamaño del chunk para no perder transiciones.
- **En texto legal:** respeta la unidad natural — un artículo, un numeral, un control del Anexo A = idealmente un chunk con su metadato. No partas un artículo a la mitad.

## 3. Recuperación (Retrieval): híbrida y con umbral
Aquí está la diferencia principal frente a un RAG genérico. Para un corpus normativo se usan **tres rutas combinadas**:

1. **Estructurada (espinazo):** filtro por `id_control` / `funcion_nist` que la pregunta ya trae. Determinista, siempre acierta, siempre citable. Es el camino primario.
2. **Densa (semántica):** embeddings Voyage (familia `voyage-3`, multilingüe) para casar **lenguaje llano del usuario ↔ jerga legal** y **español ↔ inglés** (NIST/ISO originales). Donde el espinazo no tiene etiqueta directa.
3. **Léxica (BM25):** captura identificadores y siglas exactas ("Artículo 15", "A.7.2") que lo denso a veces pierde.

- **Fusión (RRF):** combina los rankings denso + léxico con Reciprocal Rank Fusion.
- **Reranking:** pasa el top-k por un cross-encoder (Voyage `rerank-2`) que mira query+chunk juntos → gran salto de precisión.
- **Almacenamiento:** para este corpus (cientos de chunks) basta un store simple persistente — FAISS o un JSON de vectores + similitud coseno en numpy. Qdrant/ChromaDB son válidos pero sobredimensionados aquí; úsalos solo si ya los manejas. Persistir en disco evita re-indexar por sesión.
- **Top-K:** 5–15 fragmentos suele dar contexto suficiente sin saturar al LLM.
- **Umbral de abstención:** si ningún fragmento supera el score mínimo, el sistema **no genera** — devuelve "sin fundamento suficiente". Esto previene literalmente el cumplimiento cosmético y alimenta el indicador de verificabilidad.

## 4. Generación y Prompts de Control
La confiabilidad depende de qué tan estrictas sean las instrucciones.

- **Instrucción de restricción:** "Responde únicamente con base en el contexto proporcionado. Si la respuesta no está en el texto, dilo explícitamente."
- **Cita antes de concluir:** el modelo debe citar el pasaje recuperado antes de afirmar nada.
- **Salida estructurada (JSON schema):** cada recomendación obligada a llevar `id_control` y `fuente` válidos. Sin fuente → no se emite (convierte "una brecha sin control de destino no genera recomendación" en una restricción del esquema).
- **Citations nativas de Anthropic:** la API de Claude soporta *citations* — el modelo devuelve el span exacto del documento fuente para cada afirmación, con su referencia. Es la pieza individual de mayor ROI: materializa la "constancia verificable" casi gratis.
- **Sobre la "temperatura cero" (matiz importante con Claude):** temperatura baja reduce la variabilidad, pero en Claude **no garantiza determinismo bit a bit**, y al usar pensamiento extendido la temperatura puede estar restringida. No confíes el determinismo a la temperatura: la reproducibilidad real de este sistema viene del **espinazo de reglas + caché de salidas + validación de citas**, no del sampler.

## 5. Verificación y Guardrails (el diferenciador AI-safety)
Capas de defensa que revisan la salida del LLM antes de entregarla.

- **Validación de citas contra el índice (determinista):** todo artículo/control citado debe **existir realmente en el corpus**. Si el modelo inventa "Artículo 47 de la Ley 1581" inexistente → se rechaza automáticamente. Barato, determinista y muy convincente.
- **Verificador de faithfulness (LLM-as-judge):** una segunda llamada comprueba que cada afirmación generada está *entailed* por las fuentes citadas (groundedness, métrica de faithfulness de RAGAS). Si no se sostiene → se marca o elimina. Es, técnicamente, una salvaguarda de seguridad de IA.
- **Guardrails de formato/PII:** validar esquema de salida; los documentos que sube el usuario se procesan solo en sesión (consentimiento previo, Ley 1581).

## 6. Evaluación (Confiabilidad Continua)
- **Ajuste de hiperparámetros:** no adivines `chunk_size` ni `K`; prueba combinaciones sobre tu data específica.
- **Dataset de evaluación (preguntas-oro):** consultas con controles/citas esperados. Mide **retrieval recall@k**, **precisión de citas** y **faithfulness**. Da números reales para la sección de Resultados del reporte y permite testear ante cambios de modelo o corpus.

## 7. Arquitectura Recomendada
- **Ingestor:** proceso independiente que limpia, fragmenta, etiqueta metadatos y carga datos (offline, una sola vez; embeddings cacheados en JSON).
- **Base de conocimiento:** store de vectores + chunks con metadatos enriquecidos (`id_control`, `funcion_nist`, `referencia_legal`).
- **Asistente RAG:** clase modular que orquesta retrieval híbrido → rerank → construcción de prompt → llamada a Claude con citations.
- **Capa de verificación:** validación de citas + verificador de faithfulness antes de entregar al usuario.

## 8. Stack concreto para este proyecto
- **Embeddings:** Voyage AI (Anthropic no tiene API de embeddings propia). Familia `voyage-3` multilingüe. Corpus pequeño → costo dentro de la capa gratuita.
- **Generación:** Claude `claude-opus-4-8` vía SDK de Python (`anthropic`).
- **Reranking:** Voyage `rerank-2`.
- **Retrieval léxico:** BM25 (rank-bm25 o equivalente) en Python.
- **Sin base de datos pesada:** vectores cacheados en JSON / FAISS; estado solo en sesión.

---

## 9. Las tres capas de defensa anti-alucinación
El sistema apila tres barreras (modelo del "queso suizo" de Hendrycks — los huecos de una capa los tapa la siguiente):

1. **Recuperación con umbral** → si no hay fundamento, se abstiene.
2. **Generación citada y estructurada** → cada afirmación amarrada a su fuente (citations nativas).
3. **Validación determinista de citas + verificador de faithfulness** → se rechaza lo que no exista en el corpus o no esté respaldado.

Esta es la contribución de seguridad de IA del proyecto y debe destacarse en el paper.

---

## 10. Coincidencia con la guía base
| Tema | Guía base genérica | Esta versión (proyecto) |
|------|--------------------|--------------------------|
| Metadatos para filtrar | ✅ Mencionado | ✅ Convertido en espinazo determinista por `id_control` |
| Chunking semántico + overlap | ✅ | ✅ + respeto a la unidad legal (1 artículo/control = 1 chunk) |
| Umbral de similitud / abstención | ✅ | ✅ Igual |
| Prompt grounded-only | ✅ | ✅ Igual + cita-antes-de-concluir |
| Top-K 5–15 | ✅ | ✅ Igual |
| Guardrails de salida | ✅ Genérico | ✅ Concreto: validación de citas contra índice |
| Dataset de evaluación | ✅ | ✅ + métricas RAGAS (recall@k, faithfulness) |
| Retrieval híbrido (denso+BM25+estructurado, RRF) | ❌ Solo vectorial | ✅ Añadido |
| Reranking (cross-encoder) | ❌ | ✅ Añadido (Voyage rerank-2) |
| Citations nativas (span exacto) | ❌ | ✅ Añadido |
| Verificador de faithfulness (LLM-as-judge) | ❌ | ✅ Añadido |
| "Temperatura cero = determinismo" | ⚠️ Afirmado | ⚠️ Matizado: con Claude no garantiza determinismo; reproducibilidad vía reglas + caché + validación |
| Vector DB (Qdrant/Chroma/FAISS) | ✅ | ✅ Pero simplificado: para este corpus basta FAISS/JSON |
