# INFRAESTRUCTURA DEL SaaS — Playbook de IA Responsable para PYMES
> Global South AI Safety Hackathon 2026 · Track 1: Latinoamérica · Gobernanza
> Documento de infraestructura operativa. Describe **cómo funciona el sistema**: fuentes, flujo, capas de entrega y mecanismos de seguridad. Alineado a `PROPUESTAFINAL.md`.

> **Alcance:** Este documento recoge solo la **infraestructura operativa del SaaS**. El contexto teórico, regulatorio y competitivo (fundamentos académicos, matriz CONPES, diferenciación vs. fAIr LAC, hoja de ruta CIPE/CCIT, etc.) NO forma parte de la infraestructura y queda en la propuesta general (`PROPUESTAFINAL.md`, sección 7).

---

## 1. QUÉ ES (resumen operativo)

Herramienta SaaS de autodiagnóstico que, mediante un árbol de **máximo 20 preguntas** adaptadas a la realidad de una PYME, evalúa su uso de IA frente a marcos operativos internacionales (NIST AI RMF, ISO 42001) y un marco ético consolidado (UNESCO + OCDE), y entrega:
- un diagnóstico auditable de riesgos legales, éticos y de responsabilidad,
- una hoja de ruta priorizada de recomendaciones, y
- los artefactos que cierran las brechas (incluida una **política de IA generada con LLM a la medida**).

El sistema prioriza **América Latina y el Caribe** como región base y es extensible al Sur Global bajo demanda. La normativa nacional (Constitución, leyes de datos) se carga como **paquete del país** declarado por la organización; para la demo el país instanciado es **Colombia**.

**Diferenciadores operativos:**
1. **No solo diagnostica y recomienda: produce los artefactos** que cierran las brechas (políticas generadas con LLM, registros, procedimientos, constancia verificable).
2. **Indicador de verificabilidad por respuesta:** distingue lo autodeclarado de lo respaldado por evidencia documental, previniendo el "cumplimiento cosmético".

---

## 2. FUENTES NORMATIVAS Y ÉTICAS (insumo del sistema)

**Flujo de construcción:** FUENTES → PREGUNTAS → OUTPUT

Toda evaluación se fundamenta en fuentes vigentes cargadas automáticamente según la ubicación declarada. Ninguna evaluación se ejecuta sin estas fuentes activas.

### A. Fuentes internacionales obligatorias (universales, sin importar ubicación)
Proporcionan controles operativos concretos y auditables.
- **NIST AI Risk Management Framework (RMF) 1.0** + **NIST AI RMF Playbook** — aporta las 4 funciones (GOVERN, MAP, MEASURE, MANAGE) con acciones sugeridas por subcategoría. Traduce principios en controles verificables.
- **ISO 42001:2023** (y familia ISO de seguridad aplicable) — única norma internacional certificable de gestión de sistemas de IA. Aporta controles del Anexo A mapeables a brechas concretas.

### B. Fuentes éticas (universales) — 5 principios consolidados
La dispersión de marcos de ética de IA converge, siguiendo la traducibilidad de Floridi y Cowls (2019), en cuatro principios de la bioética más uno nuevo. Cada principio se robustece con los marcos regionales (UNESCO, OCDE) y distingue **lo exigible al proveedor** de **la responsabilidad del usuario** que lo emplea.

| Principio | Síntesis operativa | Consolida (UNESCO / OCDE) |
|-----------|--------------------|----------------------------|
| **Beneficencia** | El sistema debe producir un bien real y verificable, no una promesa, con atención a grupos vulnerables. | UNESCO proporcionalidad e inocuidad, gobernanza colaborativa · OCDE crecimiento inclusivo |
| **No maleficencia** | Anticipar y prevenir daños antes que repararlos; vigilancia anticipatoria de riesgos. | UNESCO seguridad y protección · OCDE solidez y seguridad |
| **Autonomía** | Las decisiones que afectan a personas permanecen bajo control humano y delegación informada. | UNESCO supervisión humana, intimidad · OCDE derechos humanos y privacidad |
| **Justicia** | Beneficios y cargas distribuidos sin discriminación; responsabilidad trazable. | UNESCO equidad y no discriminación, sostenibilidad · OCDE equidad |
| **Explicabilidad** | Inteligibilidad (¿cómo funciona?) + rendición de cuentas (¿quién responde?). Habilita a los otros cuatro. | UNESCO transparencia, rendición de cuentas · OCDE transparencia y responsabilidad |

### C. Paquete nacional (se carga según el país declarado)
Cubre los derechos fundamentales y la normativa estatutaria del país. Para la demo (Colombia):
- **Constitución Política de Colombia (1991)** — art. 13 (igualdad), 15 (habeas data), 20 (libertad de información), 29 (debido proceso).
- **Ley 1581 de 2012** — protección de datos personales (autoridad: SIC).
- **CONPES 4144 (2025)** — Política Nacional de IA (referencia de contexto nacional).
- **Normativa sectorial** — se carga según el sector declarado.

> La arquitectura replica esta estructura en otros países de la región: núcleo universal (NIST + ISO + UNESCO + OCDE) + paquete nacional (Constitución + normativa estatutaria del país).

---

## 3. EJES DE MEDICIÓN Y VECTOR DE DIAGNÓSTICO

La evaluación se estructura en **tres ejes de medición**, todos universales y portables entre países:

| Eje | Descripción |
|-----|-------------|
| **ÉTICO** (x) | Evaluación frente a los 5 principios consolidados (UNESCO/OCDE). |
| **ISO** (y) | Cobertura frente a los controles de ISO/IEC 42001. |
| **NIST** (z) | Madurez frente a las 4 funciones del NIST AI RMF. |

> Lo legal **no es un eje de medición** (es específico de cada país): se atiende vía el paquete nacional y la justificación normativa (2.3). El cumplimiento de NIST/ISO puede no ser suficiente; el eje ÉTICO los complementa.

Al final del diagnóstico, los tres ejes producen un **vector (x = ÉTICO, y = ISO, z = NIST)**, cada eje de 0 a 100, que ubica a la organización en un **espacio 3D** (diagnóstico visual). Cada pregunta puede aportar a los tres ejes según su mapeo.

**Materialización de los ejes en las capas:**

| Eje | Capa 1 (Diagnóstico) | Capa 2 (Recomendaciones) | Capa 3 (Ejecución) |
|-----|----------------------|--------------------------|---------------------|
| **ÉTICO** | 1.2 (riesgo por impacto en principios) | 2.3 (justificación de derechos y principios) | 3.2 (evaluación de impacto) |
| **ISO** | 1.4 (cobertura / brechas ISO 42001) | 2.1 (recomendación por control ISO) | 3.4 (SoA + insumos de auditoría) |
| **NIST** | 1.3 (madurez por función NIST) | 2.1 / 2.5 (recomendaciones priorizadas y secuenciadas) | 3.1 + 3.2 (políticas, plantillas) |

---

## 4. FLUJO DE LA HERRAMIENTA (4 PASOS)

| Paso | Descripción |
|------|-------------|
| **1. Contexto / Infraestructura** | El usuario registra ubicación (país) y sector → el sistema carga el núcleo universal (ISO, NIST, UNESCO, OCDE) + el paquete nacional correspondiente. **El usuario puede adjuntar voluntariamente documentos propios** que alimentan el diagnóstico y de los cuales dependen las preguntas (ver sección 7.3). |
| **2. Bifurcación inicial** | ¿Para qué usa IA? (1) Desarrollar/usar IA para productos o servicios para terceros; (2) Automatizar procesos internos; (3) Ambas. Determina el árbol, los riesgos y los controles ISO 42001 / NIST aplicables. Desarrollar productos implica obligaciones hacia terceros distintas al uso interno. |
| **3. Árbol de preguntas** | **Máximo 20 preguntas.** Cada pregunta: instrucción clara + contexto de PYME. Las ramas dependen de las respuestas anteriores. Cada pregunta mapea a al menos una función NIST, un control ISO 42001 y un principio ético. |
| **4. Generación de resultados** | Ver sección 5 (3 Capas de Entrega). |

---

## 5. OUTPUTS AL USUARIO — 3 CAPAS DE ENTREGA

### CAPA 1 — DIAGNÓSTICO (Auditable, no opinión)
**Objetivo:** Convertir las respuestas del árbol en una evaluación objetiva y auditable del estado actual frente a gobernanza de IA, cumplimiento legal, riesgos éticos y responsabilidades.

| # | Output | Fuente que lo sustenta |
|---|--------|------------------------|
| 1.1 | **Perfil y alcance del sistema de IA:** clasificación según la bifurcación inicial y delimitación del alcance evaluado. | Bifurcación del flujo |
| 1.2 | **Inventario de casos de uso de IA:** clasificación de riesgo por caso (alto/medio/bajo según impacto ético y normativo). | Control A.5 de ISO 42001 + función MAP de NIST |
| 1.3 | **Puntaje de madurez por función NIST:** GOVERN, MAP, MEASURE, MANAGE, con desagregación por subcategoría. Permite un radar de madurez visual. | NIST AI RMF |
| 1.4 | **Cobertura frente a ISO 42001:** análisis de brecha contra cláusulas 4–10 y controles del Anexo A (ausente / parcial / implementado). | ISO 42001 |
| 1.5 | **Registro de brechas priorizado (gap register):** cada brecha con severidad, control afectado, principio o riesgo comprometido. | NIST + ISO |
| 1.6 | **Indicador de verificabilidad por respuesta:** distingue lo autodeclarado de lo respaldado por evidencia documental. El usuario puede adjuntar documentos para elevar el nivel de confianza de "autodeclarado" a "verificado con evidencia". Ver sección 7.3. | Concepto propio "verificable" |

### CAPA 2 — RECOMENDACIONES (Hoja de ruta consciente de recursos)
**Objetivo:** Transformar las brechas en acciones concretas, priorizadas y justificadas, orientadas al cierre de riesgos.

| # | Output | Descripción |
|---|--------|-------------|
| 2.1 | **Recomendación por brecha** | Cada una con referencia cruzada a la subcategoría NIST y al control ISO que cierra. Una brecha sin control de destino no genera recomendación. |
| 2.2 | **Priorización por reducción de riesgo vs. esfuerzo/costo** | Matriz o puntaje. Las *quick wins* de bajo costo tienen el mismo peso que las medidas estructurales. |
| 2.3 | **Justificación normativa y de derechos** | Parte de la **Constitución Política del país** como fuente primaria de derechos fundamentales, y luego vincula la normativa estatutaria, los principios éticos, los controles ISO y las funciones NIST aplicables. |
| 2.4 | **Esfuerzo estimado y rol responsable sugerido** | Bajo / medio / alto. Define quién ejecuta considerando que una PYME no tiene CISO (ej. dueño, gerente, TI externo). |
| 2.5 | **Secuenciación por fases** | 0–30 días, 30–90 días, estructural. |
| 2.6 | **Criterio de cierre verificable por recomendación** | Qué evidencia concreta demuestra que la brecha quedó cerrada. Cierra el círculo con el indicador de verificabilidad de la Capa 1. |

**Visualización del output 2.2 (plano cartesiano):** es la visualización principal de la priorización. Los ejes **dependen de las preguntas formuladas y las respuestas del usuario**: no son fijos ni predefinidos, sino determinados dinámicamente según el contexto de la PYME, las brechas detectadas y los documentos adjuntos. Ejemplos de ejes posibles: esfuerzo/costo vs. reducción de riesgo · impacto normativo vs. probabilidad de incumplimiento · área afectada vs. consenso requerido.

### CAPA 3 — EJECUCIÓN (El SaaS produce, no solo aconseja)
**Objetivo:** Generar los artefactos que cierran las brechas detectadas.

| # | Artefacto generado | Fuente / Control |
|---|-------------------|------------------|
| 3.1 | **Políticas generadas con LLM a la medida:** política de IA, uso aceptable, supervisión humana — generadas dinámicamente a partir del contexto (país, sector, bifurcación, respuestas del árbol). | ISO 42001 A.2 / cláusula 5.2 |
| 3.2 | **Registros operativos:** inventario de sistemas de IA, matriz de riesgos, plantilla de evaluación de impacto del sistema de IA. | ISO 42001 A.5 + función MEASURE de NIST |
| 3.3 | **Procedimientos:** respuesta a incidentes de IA, gobierno de datos, gestión de IA de terceros. | ISO 42001 A.7, A.10 |
| 3.4 | **Insumos de auditoría:** borrador de Declaración de Aplicabilidad (SoA) de ISO 42001 y lista de verificación con rastro de auditoría. | ISO 42001 (cláusulas 4–10) |
| 3.5 | **Plan de implementación accionable:** tareas asignables con responsable y fecha, derivadas de la secuenciación de la Capa 2. | Capa 2 output 2.5 |
| 3.6 | **Constancia verificable:** registro con fecha y referencia de qué se evaluó, qué se encontró y qué se generó. Funciona además como **activo comercial y regulatorio** presentable ante clientes, proveedores o auditorías. | Concepto propio |

---

## 6. MAPEO NIST → CAPAS (referencia operativa de diseño)

| Función NIST | Rol en el sistema |
|--------------|-------------------|
| **GOVERN** | Capa 1 (madurez por función) + Capa 3 (políticas generadas con LLM, procedimientos) |
| **MAP** | Capa 1 (inventario de casos de uso, clasificación de riesgo) |
| **MEASURE** | Capa 1 (evaluación de impacto, indicadores de verificabilidad) + Capa 3 (plantillas de evaluación) |
| **MANAGE** | Capa 2 (recomendaciones priorizadas, secuenciación) + Capa 3 (plan de implementación) |

> El Playbook NIST se usa como **marco de traducción** entre los principios éticos (UNESCO/OCDE) y controles operativos concretos ejecutables por una PYME.

---

## 7. MECANISMOS DE SEGURIDAD Y FEEDBACK

### 7.1 Disclaimer obligatorio (siempre visible)
> "Aviso importante: Este sistema tiene fines exclusivamente informativos y de autoevaluación, y no constituye ni reemplaza asesoría legal, regulatoria o profesional especializada. El sistema no solicita información confidencial ni datos sensibles para su funcionamiento. La carga de documentos o evidencias es completamente voluntaria. Al adjuntar cualquier documento, el usuario declara y garantiza que cuenta con las autorizaciones, permisos y derechos necesarios para su tratamiento, de conformidad con la Sección 7.3."

### 7.2 Reporte de errores de afinación y alucinaciones
Mecanismo explícito para que el usuario reporte:
- Recomendaciones que no aplican a su contexto.
- Respuestas que parecen incorrectas o inventadas.
- Interpretaciones erróneas de la normativa.

**Formato del reporte:** campo libre de descripción · captura de la sección afectada · clasificación del tipo de error ((a) error normativo, (b) alucinación del modelo, (c) desajuste de contexto PYME, (d) otro) · opción de recibir respuesta por correo.

### 7.3 Subida de evidencias y fuentes adicionales por parte del usuario
Refuerza el **indicador de verificabilidad** (Capa 1.6). El usuario puede adjuntar **voluntariamente** documentos al inicio del flujo (Paso 1), antes de responder el árbol. Estos documentos alimentan tanto el diagnóstico como las preguntas, porque el sistema extrae automáticamente la información relevante para validar el cumplimiento ante los controles ISO o funciones NIST.

**Flujo:**
1. En el Paso 1 (Contexto), el usuario puede adjuntar documentos (políticas internas, contratos, registros, etc.).
2. Se muestra un **checkbox de consentimiento** que el usuario debe aceptar antes de subir archivos.
3. El sistema extrae automáticamente la información relevante.
4. Los documentos influyen en las preguntas del árbol (Paso 3) y en el nivel de verificabilidad del diagnóstico.
5. La opción de **"No adjuntar"** siempre está disponible. Sin evidencia, el sistema opera con autodeclaración (nivel de confianza: **"bajo"**).

**Declaración de consentimiento (checkbox obligatorio):**
> "Declaro que soy consciente del contenido de los documentos y cuento con los permisos y autorizaciones necesarios para su tratamiento, incluyendo la autorización del titular de datos personales conforme a la normativa aplicable y la Constitución Política de mi país."

**Restricciones técnicas:** PDF, PNG, JPG, DOCX (sin macros) · máximo 5 MB por archivo · los archivos se mantienen solo durante la sesión y la generación del informe.

---

## 8. RESUMEN EJECUTIVO DE LA ARQUITECTURA

```
┌─────────────────────────────────────────────────────────────┐
│  USUARIO (PYME del Sur Global · país declarado)             │
│  Responde árbol de ≤20 preguntas adaptadas                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
   Fuentes activas: NÚCLEO UNIVERSAL (NIST · ISO 42001 ·
   UNESCO · OCDE → 5 principios) + PAQUETE NACIONAL (país)
                       │
         ┌─────────────▼─────────────┐
         │   CAPA 1 — DIAGNÓSTICO    │  ← Auditable, no opinión
         │  • Perfil + inventario    │
         │  • Madurez NIST (radar)   │
         │  • Eje ético (5 princ.)   │
         │  • Brechas ISO 42001      │
         │  • Gap register           │
         │  • Verificabilidad        │
         └─────────────┬─────────────┘
                       │
         ┌─────────────▼─────────────┐
         │ CAPA 2 — RECOMENDACIONES  │  ← Consciente de recursos PYME
         │  • Recomendación x brecha │
         │  • Priorización riesgo/   │
         │    esfuerzo (plano        │
         │    contextual)            │
         │  • Justificación normativa│
         │  • Roles sin CISO         │
         │  • Secuencia 0-30-90      │
         │  • Criterio de cierre     │
         └─────────────┬─────────────┘
                       │
         ┌─────────────▼─────────────┐
         │  CAPA 3 — EJECUCIÓN       │  ← El SaaS produce artefactos
         │  • Políticas con LLM      │
         │  • Registros operativos   │
         │  • Procedimientos         │
         │  • Insumos auditoría      │
         │  • Plan accionable        │
         │  • Constancia verificable │
         └───────────────────────────┘
```
