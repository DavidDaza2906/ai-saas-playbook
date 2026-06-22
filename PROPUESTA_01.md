# PROPUESTA FINAL — Playbook de IA Responsable para PYMES
> Global South AI Safety Hackathon 2026 · Track 1: Latinoamérica · Gobernanza
> Diseño de arquitectura para un SaaS de autodiagnóstico, con prototipo visual y prueba de concepto documentada.

---

## 0. PITCH

**Diseño de una herramienta SaaS de autodiagnóstico** que, mediante un árbol de **máximo 20 preguntas** adaptadas a la realidad de una PYME, evalúa su uso de IA frente a normativa colombiana vigente (Constitución Política, CONPES 4144, Ley 1581) y marcos operativos internacionales (NIST AI RMF, ISO 42001), entregando un diagnóstico de riesgos legales, éticos y de responsabilidad, junto con recomendaciones y una **política de IA generada con LLM a la medida** de la organización.

**Diferenciador frente a herramientas existentes:**
1. **No solo diagnostica y recomienda: produce los artefactos** que cierran las brechas (políticas generadas con LLM, registros, procedimientos, constancia verificable).
2. **Indicador de verificabilidad por respuesta:** distingue lo autodeclarado de lo respaldado por evidencia documental, previniendo el "cumplimiento cosmético" (marcar casillas sin sustancia).

**Objetivo de fondo:** Democratizar el cumplimiento y la ética de la IA, bajando estándares internacionales al alcance de empresas pequeñas **colombianas** que no tienen equipo legal ni de riesgos. La arquitectura es **escalable a otros países de América Latina** bajo demanda.

> **Nota de alcance:** Este entregable es el **diseño completo de la arquitectura**, validado con un prototipo visual (mockup) y una prueba de concepto documentada de un caso recorriendo las 3 capas. No es un producto funcional terminado.

---

## 1. PROBLEMA QUE RESOLVEMOS

- Las PYMES adoptan IA sin saber qué obligaciones legales y éticas asumen.
- El cumplimiento normativo (NIST, ISO 42001) está pensado para grandes organizaciones con recursos.
- **Premisa clave:** la ausencia de regulación no implica ausencia de ética; y además ya existen leyes, jurisprudencia y guias aplicables.
- No cumplir implica riesgo legal, ético, reputacional, además de pérdida de competitividad.

---

## 2. FUENTES NORMATIVAS Y FLUJO DE CONSTRUCCIÓN

**Flujo:** FUENTES → PREGUNTAS → OUTPUT

### Fuentes obligatorias
> El sistema se centra en **Colombia** como país base, donde el equipo conoce la jurisprudencia y puede sustentar cada fuente con rigor. La arquitectura es escalable a otros países de América Latina replicando la misma estructura (Constitución + normativa estatutaria + estándares internacionales).

**A. Fuentes internacionales obligatorias (anclaje operativo)**
> Estas fuentes se seleccionan porque proporcionan **controles operativos concretos y auditables**, no solo principios abstractos. Son los marcos más reconocidos internacionalmente para gestión de riesgos de IA y sistemas de gestión.

- **NIST AI Risk Management Framework (RMF) 1.0** + **NIST AI RMF Playbook** — proporciona las 4 funciones (GOVERN, MAP, MEASURE, MANAGE) con acciones sugeridas por subcategoría. Se elige sobre otros marcos (ej. OECD AI Principles) porque traduce principios en controles verificables.
- **ISO 42001:2023** — única norma internacional certificable de gestión de sistemas de IA. Se elige sobre otras ISO (ej. ISO 23894) porque proporciona controles del Anexo A mapeables a brechas concretas.

**B. Fuentes colombianas obligatorias (contexto nacional)**
> Estas fuentes se seleccionan porque cubren los tres niveles del ordenamiento jurídico colombiano: Constitución (derechos fundamentales), normativa estatutaria (leyes) y política pública (CONPES). El equipo legal puede sustentar su aplicación con jurisprudencia de la Corte Constitucional.

- **Constitución Política de Colombia (1991)** — art. 15 (intimidad), art. 20 (habeas data), art. 13 (igualdad), art. 29 (debido proceso). Marco supremo que reconoce derechos fundamentales afectados por sistemas de IA.
- **CONPES 4144 (2025)** — Política Nacional de Inteligencia Artificial. Define los 5 principios de "uso responsable de la IA" que el sistema adopta como eje ético.
- **Ley 1581 de 2012** — protección de datos personales. Única norma colombiana con cadena vinculante completa (autoridad: SIC).
- **Normativa sectorial colombiana** — se carga según el sector declarado por la PYME (salud: Ley 1581 + Resolución 199 de 2016; financiero: Circular Básica Jurídica SFC; etc.).

### Fuentes contextuales opcionales (benchmark, no obligatorias)
> Estas fuentes se ofrecen como referencia comparativa. No son obligatorias para PYMES colombianas, pero el sistema puede activarlas si el usuario desea contrastar.

- **EU AI Act (Reglamento UE 2024/1689)** — referencia del enfoque basado en riesgo.
- **Hoja de Ruta CIPE/CCIT (2026)** — referencia regional que valida la necesidad del sistema (ver sección 7.6).

### Escalabilidad a otros países
> La arquitectura está diseñada para replicarse en otros países de América Latina siguiendo la misma estructura: (1) Constitución local como fuente de derechos fundamentales, (2) normativa estatutaria vigente, (3) estándares internacionales (NIST + ISO 42001). Para la demo y el paper, el alcance se limita a Colombia.

> No se trata solo de "seguir un manual", sino de cubrir también las implicaciones de las **fallas éticas**, no únicamente las legales.

---

## 3. OUTPUTS ESPERADOS (EJES)

Antes de redactar preguntas, fijamos qué entregamos. Los outputs cubren tres ejes:

| Eje | Descripción |
|-----|-------------|
| **LEGAL** | Cumplimiento normativo aplicable a la PYME según país y sector. |
| **ÉTICO** | Evaluación de riesgos para personas, derechos y equidad. |
| **RESPONSABILIDAD** | Quién responde por qué dentro de la organización. |

**Materialización de los ejes en las capas del sistema:**

| Eje | Capa 1 (Diagnóstico) | Capa 2 (Recomendaciones) | Capa 3 (Ejecución) |
|-----|----------------------|--------------------------|---------------------|
| **LEGAL** | 1.4 (brechas ISO 42001) | 2.3 (justificación normativa) | 3.4 (SoA + insumos de auditoría) |
| **ÉTICO** | 1.2 (clasificación de riesgo por impacto en derechos) | 2.3 (derechos fundamentales) | 3.2 (evaluación de impacto) |
| **RESPONSABILIDAD** | 1.1 (perfil y alcance) | 2.4 (rol responsable sugerido) | 3.5 (plan con responsable y fecha) |

---

## 4. FLUJO DE LA HERRAMIENTA (4 PASOS)

| Paso | Descripción |
|------|-------------|
| **1. Contexto / Infraestructura** | Ubicación (Colombia como país base) y sector → carga las fuentes normativas correspondientes: Constitución Política de Colombia, CONPES 4144, Ley 1581, NIST AI RMF, ISO 42001. **En este paso el usuario puede adjuntar voluntariamente documentos propios** que alimentan el diagnóstico y del cual dependen las preguntas que se formularán (ver sección 6.3). |
| **2. Bifurcación inicial** | ¿Usted utiliza IA para...? (1) Desarrollar productos o servicios para la sociedad; (2) Automatizar procesos internos; (3) Ambas. Según la respuesta se despliega el árbol de preguntas que asegura el cumplimiento de ISO 42001 y NIST. Esta clasificación impacta las **responsabilidades legales, de riesgo y los controles ISO/NIST aplicables**, ya que desarrollar productos con IA implica obligaciones hacia terceros (usuarios, clientes) distintas a las del uso interno. |
| **3. Árbol de preguntas** | **Máximo 20 preguntas.** Cada pregunta: instrucción clara + contexto de PYME. Las ramas dependen de las respuestas anteriores. Cada pregunta debe mapear a al menos una función NIST o control ISO 42001. |
| **4. Generación de resultados** | Ver sección 5 (3 Capas de Entrega). |

---

## 5. OUTPUTS AL USUARIO — 3 CAPAS DE ENTREGA

### CAPA 1 — DIAGNÓSTICO (Auditable, no opinión)

**Objetivo:** Convertir las respuestas del árbol de 20 preguntas en una imagen del estado actual que sea auditable.

| # | Output | Fuente que lo sustenta |
|---|--------|------------------------|
| 1.1 | **Perfil y alcance del sistema de IA:** clasificación de la organización según la bifurcación inicial y delimitación del alcance evaluado. Sin esto, la madurez no es comparable entre empresas. | Bifurcación del flujo |
| 1.2 | **Inventario de casos de uso de IA:** clasificación de riesgo por caso (alto/medio/bajo según impacto en personas y derechos). | Control A.5 de ISO 42001 + función MAP de NIST |
| 1.3 | **Puntaje de madurez por función NIST:** GOVERN, MAP, MEASURE, MANAGE, con desagregación por subcategoría. Permite un radar de madurez visual. | NIST AI RMF |
| 1.4 | **Cobertura frente a ISO 42001:** análisis de brecha contra cláusulas 4–10 y controles del Anexo A, indicando estado por control (ausente / parcial / implementado). | ISO 42001 |
| 1.5 | **Registro de brechas priorizado (gap register):** cada brecha con severidad, control afectado, derecho o riesgo comprometido. | NIST + ISO |
| 1.6 | **Indicador de verificabilidad por respuesta:** distingue entre lo autodeclarado y lo respaldado por evidencia documental, reflejando el nivel de confianza en el diagnóstico. El usuario puede adjuntar documentos propios (fuentes internas) para elevar el nivel de confianza de "autodeclarado" a "verificado con evidencia". Ver sección 6.3 para el flujo de consentimiento y protección de datos al subir archivos. | Concepto propio "verificable" |

---

### CAPA 2 — RECOMENDACIONES (Hoja de ruta consciente de recursos)

**Objetivo:** Convertir brechas en una hoja de ruta priorizada, crítico para PYMES con capacidad limitada.

| # | Output | Descripción |
|---|--------|-------------|
| 2.1 | **Recomendación por brecha** | Cada una con referencia cruzada a la subcategoría NIST y al control ISO que cierra. Una brecha sin control de destino no genera recomendación. |
| 2.2 | **Priorización por reducción de riesgo vs. esfuerzo/costo** | Matriz o puntaje. Las *quick wins* de bajo costo tienen el mismo peso que las medidas estructurales. |
| 2.3 | **Justificación normativa y de derechos** | Por qué importa, qué riesgo o derecho fundamental atiende, y qué requisito del marco satisface. La justificación siempre parte de la **Constitución Política de Colombia** como fuente primaria de derechos fundamentales, y luego vincula la normativa estatutaria (Ley 1581, CONPES 4144), los controles ISO y las funciones NIST aplicables. |
| 2.4 | **Esfuerzo estimado y rol responsable sugerido** | Bajo / medio / alto. Define quién ejecuta considerando que una PYME no tiene CISO (ej. dueño, gerente, equipo de TI externo). |
| 2.5 | **Secuenciación por fases** | 0–30 días, 30–90 días, estructural. |
| 2.6 | **Criterio de cierre verificable por recomendación** | Qué evidencia concreta demuestra que la brecha quedó cerrada. Cierra el círculo con el indicador de verificabilidad de la Capa 1. |

#### Sobre el plano cartesiano (visualización del output 2.2)
El plano cartesiano es la **visualización principal** del output 2.2 (priorización). Los ejes **dependen de las preguntas formuladas y las respuestas del usuario**: no son fijos ni predefinidos, sino que el sistema los determina dinámicamente según el contexto de la PYME, las brechas detectadas y los documentos adjuntos.

> Ejemplos de ejes posibles: esfuerzo/costo vs. reducción de riesgo · impacto normativo vs. probabilidad de incumplimiento · área afectada vs. consenso requerido. La selección es arbitraria y contextual, no un menú cerrado.

---

### CAPA 3 — EJECUCIÓN (El SaaS produce, no solo aconseja)

**Objetivo:** Generar los artefactos que cierran las brechas detectadas. La calidad de ejecución que evalúan los jueces se hace tangible aquí.

| # | Artefacto generado | Fuente / Control |
|---|-------------------|------------------|
| 3.1 | **Políticas generadas con LLM a la medida:** política de IA, uso aceptable, supervisión humana — generadas dinámicamente con LLM a partir del contexto de la organización (país, sector, bifurcación, respuestas del árbol). | ISO 42001 A.2 / cláusula 5.2 |
| 3.2 | **Registros operativos:** inventario de sistemas de IA, matriz de riesgos, plantilla de evaluación de impacto del sistema de IA. | ISO 42001 A.5 + función MEASURE de NIST |
| 3.3 | **Procedimientos:** respuesta a incidentes de IA, gobierno de datos, gestión de IA de terceros. | ISO 42001 A.7, A.10 |
| 3.4 | **Insumos de auditoría:** borrador de Declaración de Aplicabilidad (SoA) de ISO 42001 y lista de verificación con rastro de auditoría. | ISO 42001 (cláusulas 4–10) |
| 3.5 | **Plan de implementación accionable:** tareas asignables con responsable y fecha, derivadas de la secuenciación de la Capa 2. | Capa 2 output 2.5 |
| 3.6 | **Constancia verificable:** registro con fecha y referencia de qué se evaluó, qué se encontró y qué se generó. Materialización del adjetivo "verificable". Además, funciona como **activo comercial y regulatorio** que la PYME puede presentar ante clientes, proveedores o auditorías para demostrar credibilidad en su uso de IA. | Concepto propio |

---

## 6. MECANISMOS DE SEGURIDAD Y FEEDBACK

### 6.1 Disclaimer obligatorio (siempre visible)
> "Esto no reemplaza asesoría legal profesional. El sistema no solicita datos confidenciales. La subida de evidencias documentales es **completamente voluntaria**: al adjuntar un documento, el usuario declara y garantiza que cuenta con los permisos y autorizaciones necesarios para su tratamiento (ver sección 6.3)."

### 6.2 Reporte de errores de afinación y alucinaciones
El sistema incluirá un mecanismo explícito para que el usuario reporte:
- Recomendaciones que no aplican a su contexto.
- Respuestas del sistema que parecen incorrectas o inventadas.
- Interpretaciones erróneas de la normativa.

**Formato del reporte:**
- Campo libre de descripción del error.
- Captura de la sección afectada.
- Clasificación del tipo de error: (a) error normativo, (b) alucinación del modelo, (c) desajuste de contexto PYME, (d) otro.
- Opción de recibir respuesta por correo.

> Este mecanismo refuerza la confianza, permite mejorar el sistema iterativamente y demuestra conciencia de los riesgos de los LLM —alineado con el espíritu del hackathon.

### 6.3 Subida de evidencias y fuentes adicionales por parte del usuario

Para reforzar el **indicador de verificabilidad** (Capa 1.6), el sistema permite al usuario adjuntar **voluntariamente** documentos al inicio del flujo (Paso 1), antes de responder el árbol de preguntas. Estos documentos alimentan tanto el diagnóstico como las preguntas que se formularán, ya que el sistema extrae automáticamente la información relevante para validar el cumplimiento ante los controles ISO o funciones NIST correspondientes.

**Flujo:**
1. En el Paso 1 (Contexto), el usuario puede adjuntar documentos (políticas internas, contratos, registros, etc.).
2. Se muestra un **checkbox de consentimiento** que el usuario debe aceptar antes de subir archivos.
3. El sistema extrae automáticamente la información relevante de los documentos.
4. Los documentos influyen en las preguntas del árbol (Paso 3) y en el nivel de verificabilidad del diagnóstico.
5. La opción de **"No adjuntar"** siempre está disponible. Si el usuario no adjunta evidencia, el sistema opera con autodeclaración (nivel de confianza: **"bajo"**).

**Declaración de consentimiento (checkbox obligatorio):**
> "Declaro que soy consciente del contenido de los documentos y cuento con los permisos y autorizaciones necesarios para su tratamiento, incluyendo la autorización del titular de datos personales conforme a la Ley 1581 de 2012 y la Constitución Política de Colombia."

**Restricciones técnicas:** PDF, PNG, JPG, DOCX (sin macros) · máximo 5 MB por archivo · los archivos se mantienen solo durante la sesión y la generación del informe.

> El texto legal completo del consentimiento (con referencias a la Constitución de Colombia) se incluye en el reporte de investigación como consideración de diseño.

---

## 7. CONTEXTO PARA EL USUARIO (No infraestructura del sistema)

> Esta sección proporciona contexto teórico, regulatorio y competitivo para quienes usen o evalúen el sistema. No forma parte de la infraestructura operativa del SaaS.

### 7.1 Fundamentos Teóricos
La arquitectura del sistema se apoya en los siguientes fundamentos académicos y marcos conceptuales:
- **Floridi (2023):** la explicabilidad incluye la rendición de cuentas (accountability). Respalda que la trazabilidad de decisiones no es opcional sino parte integral de la gobernanza de IA.
- **Mittelstadt (2019) y Jobin:** documentan la brecha principio-práctica en ética de la IA —los principios éticos no se traducen automáticamente en obligaciones operativas. El sistema de 3 capas responde exactamente a esta brecha.
- **Hendrycks (2024, cap. 4):** modelo del queso suizo (capas de control con huecos que se alinean). Justifica por qué un solo control no basta y se necesita un sistema integral de diagnóstico, recomendación y ejecución.
- **UNESCO / Gutiérrez (2024):** clasificación de 9 enfoques regulatorios y documentación de vacíos normativos en la región.
- **Richards, Benn & Zilka (Cambridge, 2025, arXiv:2505.04291):** análisis de incidentes y accountability, aunque sin método replicable ni contexto colombiano —lo cual deja abierto el nicho que este sistema llena.

### 7.2 Contexto Regulatorio: Matriz de Trazabilidad CONPES 4144
El sistema opera en un contexto donde la normativa de IA en Colombia (y América Latina) presenta vacíos estructurales. A modo de referencia para el usuario, se presenta la matriz de trazabilidad de los 5 principios del CONPES 4144 / marco "Uso responsable de la IA":

| Principio | ¿Norma vinculante? | ¿Quién la hace cumplir? | Tipo de vacío |
|-----------|-------------------|------------------------|---------------|
| 1. Centralidad humana / supervisión humana | Parcial | Sin autoridad clara | Vacío institucional |
| 2. Transparencia, explicabilidad y rendición de cuentas | No | Autorregulación | Vacío normativo |
| 3. Equidad y no discriminación | Parcial | Sin mecanismo de sanción | Vacío de enforceability |
| 4. Privacidad, gobernanza de datos y seguridad | **Sí** | SIC (Ley 1581/2012) | **Cadena completa** |
| 5. Robustez, fiabilidad y seguridad | No | Estándares voluntarios | Vacío técnico-normativo |

**Hallazgo clave:** solo el principio de privacidad/datos tiene cadena vinculante completa. Los demás principios carecen de mecanismos de enforceability, lo que justifica la necesidad de un sistema que transforme principios en controles operativos **auditables** (ISO 42001 + NIST).

> **Nota:** La Ley 1581/2012 regula el tratamiento de datos personales en Colombia, pero la normativa de datos personales NO cubre daños derivados de decisiones automatizadas sin base en datos personales (ej. errores en procesos internos de pymes). Esto amplía el alcance del sistema más allá del cumplimiento estricto de datos.

### 7.3 Diferenciación vs. Herramientas Existentes (fAIr LAC del BID)
Es relevante contextualizar que existen herramientas de autoevaluación ética de IA en la región, como **fAIr LAC (3S Ethical AI Self-Assessment, BID Lab)**. Las diferencias operativas clave de este sistema son:

1. **fAIr LAC diagnostica y recomienda;** este sistema además **PRODUCE los artefactos** que cierran las brechas (Capa 3: políticas generadas con LLM, registros, procedimientos, SoA, constancia verificable).
2. **Indicador de verificabilidad:** este sistema distingue lo declarado de lo probado con evidencia documental; fAIr LAC no tiene este mecanismo.
3. **Anclaje operativo en ISO 42001 + NIST:** controles concretos y auditables, no solo principios éticos abstractos.
4. **Diseño consciente de PYMES:** roles realistas (sin CISO), quick wins, secuenciación por fases, y priorización por esfuerzo/costo.

> **Contexto de evaluación:** dos juezas del hackathon (María Paula Mujica y Mónica Ulloa) tienen afiliación con el BID Lab. Esta diferenciación debe quedar clara en el reporte para evitar que el proyecto sea percibido como redundante con fAIr LAC.

### 7.4 Críticas Esperadas y Respuestas
Para anticipar objeciones de revisores y jueces:

1. **"¿Qué aporta vs. herramientas existentes?"**
   → Generación de artefactos verificables + indicador de verificabilidad + anclaje ISO/NIST operativo.

2. **"Esto promueve cumplimiento cosmético."**
   → El indicador de verificabilidad distingue declarado de probado. El output no es un "sello de aprobado" sino un perfil con acciones pendientes, brechas documentadas y criterios de cierre.

3. **"¿Qué pasa después de la evaluación?"**
   → Las Capas 2 y 3 cierran el ciclo: hoja de ruta priorizada + artefactos generados + plan accionable con fechas y responsables.

4. **"Esto puede ser un obstáculo para pymes."**
   → Priorización por esfuerzo/costo, quick wins de bajo costo, roles sin CISO, y secuenciación por fases (0-30-90 días) hacen el cumplimiento progresivo y viable.

### 7.5 NIST AI RMF Playbook como referencia operativa
El sistema se ancla en el **NIST AI Risk Management Framework (AI RMF 1.0)** y su **Playbook** complementario como capa operativa de controles concretos. El Playbook proporciona acciones sugeridas para cada subcategoría de las cuatro funciones, las cuales se resumen a continuación como contexto de diseño:

| Función NIST | Descripción del Playbook | Rol en el sistema |
|--------------|--------------------------|-------------------|
| **GOVERN** | Políticas, procesos, procedimientos y prácticas relacionadas con el mapeo, medición y gestión de riesgos de IA están establecidos, son transparentes e implementados efectivamente. | Capa 1 (madurez por función) + Capa 3 (políticas generadas con LLM, procedimientos) |
| **MAP** | El contexto se establece y se comprende. Casos de uso, usuarios, impactos y supuestos del sistema de IA se documentan. | Capa 1 (inventario de casos de uso, clasificación de riesgo) |
| **MEASURE** | Se identifican y aplican métodos y métricas apropiadas para evaluar riesgos de IA. | Capa 1 (evaluación de impacto, indicadores de verificabilidad) + Capa 3 (plantillas de evaluación) |
| **MANAGE** | Los riesgos de IA se priorizan, responden y gestionan con base en evaluaciones de Map y Measure. | Capa 2 (recomendaciones priorizadas, secuenciación) + Capa 3 (plan de implementación) |

> **Relevancia para el diseño:** El Playbook es una guía voluntaria de acciones sugeridas, no un checklist obligatorio. El sistema la utiliza como **marco de traducción** entre principios éticos (CONPES 4144) y controles operativos concretos que una PYME puede ejecutar. Esto refuerza el anclaje operativo del sistema frente a herramientas que solo diagnostican principios sin accionables.

### 7.6 Hoja de Ruta CIPE/CCIT (2026): Validación regional de la necesidad

El documento **"Hoja de ruta para la gobernanza de la IA en el sector privado de América Latina"** (CIPE, CCIT, ACTI, COMEX, 2026) valida empíricamente la necesidad que este sistema aborda. Su director es **Germán López-Ardila** (CCIT), quien además es **juez del hackathon**.

Propone una Plataforma Regional del sector privado sobre IA: un espacio de coordinación bottom-up (no regulatorio) para fortalecer la gobernanza de IA en LATAM, con énfasis en MiPymes. Su plan de acción (12–18 meses) incluye un **Toolkit de IA para MiPymes** (gestión de riesgos, gobernanza de datos, evaluación de impactos), alineado con ISO 42001.

**Alineación con este sistema:**

| Aspecto | Hoja de Ruta CIPE/CCIT | Este sistema (Playbook SaaS) |
|---------|------------------------|-------------------------------|
| Público objetivo | MiPymes del sector privado en LATAM | ✅ Idéntico |
| Necesidad | Falta de herramientas prácticas para MiPymes | ✅ Idéntica |
| Enfoque | Bottom-up, desde empresas | ✅ Idéntico |
| Estándar citado | ISO 42001 | ✅ Idéntico |
| Producto planificado | Toolkit de IA para MiPymes | Playbook SaaS de autodiagnóstico (diseñado) |

**Posicionamiento estratégico:** Este sistema es una **implementación operativa concreta** del "Toolkit de IA para MiPymes" que la hoja de ruta planifica pero aún no ha construido. Mientras la Plataforma Regional coordina a nivel macro, este sistema entrega el producto a nivel micro (PYME individual).

> Citar este documento demuestra alineación con el pensamiento de gobernanza regional que el juez Germán López-Ardila lidera, y que el proyecto responde a una agenda regional ya consensuada.

---

## 8. VALOR / IMPACTO (para la presentación)

- **Impacto social:** democratizar el acceso a la IA responsable.
- **Competitividad:** cumplir abre mercados y reduce riesgo.
- **Contextualización regional (país/sector):** diferenciador frente a frameworks genéricos del Norte Global.
- **Alineado con el objetivo de la hackathon:** traer al Sur Global al centro de la seguridad de la IA.
- **Validación regional documentada:** el sistema responde a una necesidad identificada y consensuada en la Hoja de Ruta CIPE/CCIT (2026) para gobernanza de IA en el sector privado de América Latina, alineándose con el eje de "Desarrollo de capacidades y formación para MiPymes" y con el producto "Toolkit de IA para MiPymes" planificado en esa agenda regional.

---

## 9. PENDIENTES RESUELTOS Y ABIERTOS

### ✅ Resueltos

| Pendiente | Resolución |
|-----------|------------|
| ¿De dónde sacar la metodología de Evaluación de Impacto? | Control A.5 de ISO 42001 + función MAP de NIST. Plantilla generada en Capa 3 output 3.2. |
| ¿Qué fuente respalda el "mínimo legal"? | Justificación normativa cruzada NIST/ISO en Capa 2 output 2.3 + SoA ISO 42001 en Capa 3 output 3.4. |
| ¿Variables exactas del plano cartesiano? | Arbitrarias: dependen de las preguntas formuladas y las respuestas del usuario. No son fijas ni predefinidas (ver Capa 2). |
| Número de preguntas | **Máximo 20.** Mantenido como restricción de diseño. |
| ¿Qué pasa con los derechos fundamentales no codificados en leyes ordinarias? | **Constitución Política de Colombia como fuente obligatoria.** Se carga automáticamente. La arquitectura permite replicar este enfoque en otros países. |

### ⏳ Aún abiertos (para construir este fin de semana)

| # | Tarea | Prioridad |
|---|-------|-----------|
| 1 | Diagramar el árbol de preguntas completo (ramas 1/2/3). | **ALTA** |
| 2 | Mapear normativa sectorial colombiana para la demo. | **ALTA** |
| 3 | Diseñar prototipo visual/mockup del recorrido de las 3 capas. | **ALTA** |
| 4 | Documentar prueba de concepto de un caso recorriendo las 3 capas. | **ALTA** |
| 5 | Preparar reporte PDF de investigación (plantilla Apart). | **ALTA** |
| 6 | Preparar pitch de 3 minutos para showcase domingo 7 PM. | **MEDIA** |
| 7 | Verificar artículo por artículo la **Ley 1581 de 2012** (protección de datos personales) como norma vinculante de referencia para el contexto colombiano. | **MEDIA** |

---

## 10. RESUMEN EJECUTIVO DE LA ARQUITECTURA

```
┌─────────────────────────────────────────────────────────────┐
│  USUARIO (PYME colombiana)                                  │
│  Responde árbol de ≤20 preguntas adaptadas                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────▼─────────────┐
         │   CAPA 1 — DIAGNÓSTICO    │  ← Auditable, no opinión
         │  • Perfil + inventario    │
         │  • Madurez NIST (radar)   │
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
         │  • Políticas con LLM    │
         │  • Registros operativos   │
         │  • Procedimientos         │
         │  • Insumos auditoría      │
         │  • Plan accionable        │
         │  • Constancia verificable │
         └───────────────────────────┘
```

---

## 11. NOTAS SOBRE EL REPORTE DE ENTREGA (Apart Research)

Para el equipo, recordatorio de la estructura del reporte PDF:
- **Plantilla oficial de Apart Research**, obligatoria.
- **Reporte PDF, ~4 páginas** (sin contar referencias/apéndice). Reparto sugerido: Intro+Trabajo relacionado 1p, Métodos+Resultados 2.5p, Discusión 0.5p.
- **Abstract máx. 150 palabras.**
- **Estructura:** Introducción · Trabajo relacionado · Metodología · Resultados · Discusión y limitaciones · Conclusión · Code and Data · Author Contributions · Referencias · Apéndice.
- **Sobre "Code and Data":** como el sistema es diseño/mockup (no funcional), esta sección del reporte incluirá el código del prototipo visual (si existe) y/o los datos de la prueba de concepto documentada (caso recorriendo las 3 capas). Si no hay código ejecutable, se explica que es diseño sin implementación funcional.
- **Sección OBLIGATORIA:** "Limitaciones y consideraciones de doble uso".
- **"LLM Usage Statement"** obligatorio.
- **Al menos una figura:** sugerido radar de madurez NIST y/o diagrama del recorrido de las 3 capas.
- **Idioma:** español permitido sin penalización. Evitar texto en cursiva. Citas formato libre pero consistente.
- **Entrega:** domingo 21 junio 7:00 PM hora Colombia (hard deadline del hub).
- **Evaluación (1–5 cada una):** impacto/innovación; calidad de ejecución; presentación/claridad.

---

