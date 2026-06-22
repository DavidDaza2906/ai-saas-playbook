# PROPUESTA FINAL — Playbook de IA responsable para PYMES

**Global South AI Safety Hackathon 2026 · Track 1: Latinoamérica · Gobernanza**

Diseño de arquitectura para un SaaS de autodiagnóstico, con prototipo visual y prueba de concepto documentada.

## PITCH

Diseño de una herramienta SaaS de autodiagnóstico que, mediante un árbol de máximo 20 preguntas adaptadas a la realidad de una PYME, evalúa su uso de IA frente a normativa vigente (UNESCO, OCDE, NIST AI RMF, ISO 42001) y entrega un diagnóstico de riesgos legales, éticos y de responsabilidad, junto con recomendaciones y una política de IA generada con LLM a la medida de la organización.

**Diferenciador frente a herramientas existentes:**

- No solo diagnostica y recomienda: produce los artefactos que cierran las brechas (políticas generadas con LLM, registros, procedimientos, constancia verificable).
- **Indicador de verificabilidad por respuesta:** distingue lo autodeclarado de lo respaldado por evidencia documental (que deberá ser subida obligatoriamente), previniendo el "cumplimiento cosmético" (marcar casillas sin sustancia).

**Objetivo de fondo:** Democratizar el cumplimiento y la ética de la IA, bajando estándares internacionales al alcance de empresas pequeñas de América Latina y el Caribe que no tienen equipo legal ni de riesgos. El sistema es extensible al Sur Global bajo demanda.

> **Nota de alcance:** Este entregable es el diseño completo de la arquitectura, validado con un prototipo visual (mockup) y una prueba de concepto documentada de un caso recorriendo las 3 capas. No es un producto funcional terminado.

## PROBLEMA QUE RESOLVEMOS

La adopción de inteligencia artificial por parte de las PYMES suele realizarse sin una evaluación adecuada de los riesgos legales, éticos y de gobernanza, lo que puede generar incumplimientos normativos, afectaciones a derechos fundamentales y pérdida de confianza de clientes y usuarios. El cumplimiento normativo (NIST, ISO 42001) está pensado para grandes organizaciones con recursos.

**Premisa clave:** la ausencia de regulación no implica ausencia de ética; y además ya existen leyes, guías y jurisprudencias aplicables. No cumplir implica riesgo legal, ético, reputacional, además de pérdida de competitividad.

## FUENTES NORMATIVAS Y ÉTICAS Y FLUJO DE CONSTRUCCIÓN

**Flujo:** `FUENTES → PREGUNTAS → OUTPUT`

### Fuentes obligatorias

#### Fuentes normativas

El sistema prioriza América Latina y el Caribe como región base. Toda evaluación debe fundamentarse en fuentes normativas y marcos de referencia vigentes, cargados automáticamente según la ubicación declarada por la organización. Ninguna evaluación podrá ejecutarse sin estas fuentes activas.

**A. Fuentes internacionales obligatorias (universales, sin importar ubicación):**

1. **NIST AI Risk Management Framework (RMF) 1.0.** NIST AI RMF Playbook — referencia operativa obligatoria con acciones sugeridas por subcategoría de cada función (GOVERN, MAP, MEASURE, MANAGE). El Playbook traduce los principios del RMF en controles concretos y verificables.
2. **ISO 42001:2023** (gestión de sistemas de IA) y familia ISO de seguridad aplicable.

**B. Fuentes éticas**, que provienen de dos documentos generalmente aceptados en países latinoamericanos como recomendaciones de uso y construcción y que se ven representadas en cinco principios únicos. El background ético como necesario parte del Principio de evaluación: *La ausencia de regulación específica sobre inteligencia artificial no implica ausencia de obligaciones.*

### Fuentes éticas

La proliferación de marcos de ética de la IA —internacionales, regionales y nacionales— produce cientos de principios que en gran medida se solapan y que, enunciados por separado, vuelven inmanejable cualquier diagnóstico. Siguiendo la traducibilidad propuesta por Luciano Floridi (Floridi y Cowls, 2019), esa dispersión converge sin pérdida en cuatro principios de la bioética: beneficencia, no maleficencia, autonomía y justicia, más uno nuevo: la **explicabilidad**. Consolidar en estos cinco no recorta el contenido normativo: lo ordena y lo hace operable.

Los principios conservan carácter general; en el contexto de aplicación de la herramienta se distingue, dentro de cada principio, lo que corresponde exigir y verificar al proveedor y lo que corresponde al uso responsable por parte de quien lo emplea.

A continuación, se presentan los cinco principios definidos bajo el contexto latinoamericano, cada principio se robustece en base a distintos marcos éticos propuestos en la región (OCDE, UNESCO).

#### UNESCO — 5 principios

| Principio UNESCO | Principio(s) consolidado(s) |
|---|---|
| Proporcionalidad e inocuidad | Beneficencia + No Maleficencia |
| Seguridad y protección | Beneficencia + Explicabilidad |
| Equidad y No discriminación | Justicia |
| Sostenibilidad | Justicia |
| Derecho a la intimidad y protección de datos | Autonomía + No maleficencia |
| Supervisión y decisión humanas | Autonomía + Explicabilidad |
| Transparencia y explicabilidad | Explicabilidad |
| Responsabilidad y rendición de cuentas | Explicabilidad |
| Sensibilización y educación | Justicia |
| Gobernanza y colaboración adaptativas y de múltiples partes interesadas | Justicia + Beneficencia |

#### OCDE

| Principio OCDE | Principio(s) consolidado(s) |
|---|---|
| Crecimiento inclusivo, desarrollo sostenible y bienestar | Beneficencia + Autonomía + Justicia |
| Respetar el Estado de derecho, los derechos humanos, y los valores democráticos, incluidas la equidad y la privacidad | Beneficencia + Autonomía + Justicia + Explicabilidad |
| Transparencia y explicabilidad | Explicabilidad + Autonomía |
| Solidez, seguridad y protección | No maleficencia |
| Responsabilidad | Explicabilidad + beneficencia |

#### Los cinco principios

**Beneficencia.** El uso de un sistema de IA debe producir un bien real y verificable, no una mera promesa de beneficio (no sólo para quien lo emplea, sino para la comunidad afectada) con especial atención a grupos vulnerables. Corresponde al proveedor precisar para qué sirve la herramienta, en qué condiciones y a quién beneficia; y corresponde a quien la emplea comprobar que ese bien es efectivo en su contexto, absteniéndose de usarla cuando no lo sea.

- *Responsabilidades del usuario:* juzgar si lo que la herramienta entrega es efectivamente útil, correcto y apropiado para el contexto real de aplicación, y descartar su uso cuando no lo sea.

**No maleficencia.** Los daños deben anticiparse y prevenirse antes que repararse. Debe haber una vigilancia anticipatoria sobre daños individuales, colectivos, intergeneracionales y sistémicos. Corresponde al proveedor evaluar los riesgos antes del despliegue, en proporción a su gravedad posible, y acreditar las salvaguardas correspondientes; y corresponde a quien la emplea conocer la herramienta lo suficiente para advertir cuándo su resultado es erróneo o sesgado y para no introducir en ella datos privados que no deban utilizarse.

- *Responsabilidades del usuario:* conocer suficientemente la herramienta para reconocer cuándo su resultado es erróneo, sesgado o inapropiado, y abstenerse de introducir en ella datos privados o que no deban utilizarse.

**Autonomía.** Las decisiones que afectan a las personas deben permanecer bajo control humano: las personas que puedan verse afectadas deben poder conservar el control sobre las decisiones que les atañen y la capacidad de un juicio informado sobre cuándo y cómo delegar en el sistema.

- *Responsabilidades del usuario:* ejercer ese control de forma efectiva, decidiendo de manera informada el grado de delegación y reservando la decisión humana en los usos de mayor riesgo.

**Justicia.** Los beneficios y las cargas del uso de la IA deben distribuirse de forma equitativa, sin discriminación por sexo, raza, religión, discapacidad, edad u orientación sexual. La responsabilidad sea trazable: Corresponde al proveedor acreditar que el sistema no discrimina y cómo controla los sesgos; y corresponde a quien la emplea documentar su uso, de modo que pueda reconstruirse qué ocurrió y a quién corresponde responder.

- *Responsabilidades del usuario:* documentar y hacer transparente el propio uso, de modo que la cadena de responsabilidad sea trazable.

**Explicabilidad.** Condición que habilita a los otros cuatro principios y se articula en dos preguntas: la inteligibilidad (¿cómo funciona?) y la rendición de cuentas (¿quién responde por cómo funciona?). Sin ella, la beneficencia no distingue el bien real de un proxy, la no maleficencia no traza la causa del daño, la autonomía no funda una delegación informada y la justicia se vuelve inauditable.

- *Responsabilidades del usuario:* una obligación que excede lo individual y se vuelve institucional: crear y sostener las condiciones para que quienes usan la herramienta puedan comprenderla, cuestionarla y emplearla responsablemente.

## OUTPUTS ESPERADOS (EJES)

Antes de generar preguntas, el sistema debe tener claramente definidos los resultados que entregará. La evaluación se estructura en **tres ejes de medición: ÉTICO, NIST e ISO**. El cumplimiento de los marcos operativos (NIST, ISO) puede no ser suficiente por sí solo, por lo que el eje ÉTICO los complementa; los tres conforman un marco general y portable entre países (a diferencia de lo legal, específico de cada país, que se atiende vía el paquete nacional y la justificación normativa, output 2.3).

- **EJE ÉTICO:** evaluación frente a los 5 principios consolidados (UNESCO/OCDE).
- **EJE NIST:** madurez frente a las 4 funciones del NIST AI RMF (GOVERN, MAP, MEASURE, MANAGE).
- **EJE ISO:** cobertura frente a los controles de ISO/IEC 42001.

Al final del diagnóstico, los tres ejes producen un **vector (x = ÉTICO, y = ISO, z = NIST)**, cada eje de 0 a 100, que ubica a la organización en un **espacio 3D** (diagnóstico visual). Cada pregunta puede aportar a los tres ejes simultáneamente según su mapeo.

### Materialización de los ejes en las capas del sistema

| Eje | Capa 1 (Diagnóstico) | Capa 2 (Recomendaciones) | Capa 3 (Ejecución) |
|---|---|---|---|
| **ÉTICO** | 1.2 (riesgo por impacto en principios) + eje ÉTICO del vector | 2.3 (justificación de derechos y principios) | 3.2 (evaluación de impacto) |
| **NIST** | 1.3 (madurez por función NIST) + eje NIST del vector | 2.1 / 2.5 (recomendaciones priorizadas y secuenciadas) | 3.1 (políticas) + 3.2 (plantillas) |
| **ISO** | 1.4 (cobertura / brechas ISO 42001) + eje ISO del vector | 2.1 (recomendación por control ISO) | 3.4 (SoA + insumos de auditoría) |

## FLUJO DE LA HERRAMIENTA (4 PASOS)

| Paso | Descripción |
|---|---|
| **1. Contexto / Infraestructura** | El usuario registra ubicación (país) y sector. El sistema carga automáticamente las fuentes de ISO, NIST AI RMF, UNESCO y OCDE. El usuario puede adjuntar voluntariamente documentos propios (políticas internas, contratos, registros u otros soportes), que alimentan el diagnóstico y del cual dependen las preguntas que se formularán (ver sección 6.3). |
| **2. Bifurcación inicial** | El sistema identifica el tipo de uso de IA: (1) Desarrollar/Usar sistemas de IA para desarrollar productos o servicios para terceros; (2) Utilizar sistemas de IA para automatizar procesos internos; (3) Ambas 1 y 2. Esta clasificación determina el árbol de preguntas, los riesgos asociados y los controles aplicables según NIST AI RMS e ISO 42001. |

Esta clasificación impacta las responsabilidades legales, de riesgo y los controles ISO 42001 / NIST AI RMF aplicables, ya que desarrollar productos con IA implica obligaciones hacia terceros (usuarios, clientes) distintas a las del uso interno.

| Paso | Descripción |
|---|---|
| **3. Árbol de preguntas** | Máximo 20 preguntas. Cada pregunta debe incluir contexto para PYMES. Las ramas dependen de las respuestas anteriores. Cada pregunta debe mapear a al menos una función NIST AI RMF o control ISO 42001. |
| **4. Generación de resultados** | El sistema genera los outputs definidos en las tres capas de entrega. Ver sección 5 (3 Capas de Entrega). |

## OUTPUTS AL USUARIO — 3 CAPAS DE ENTREGA

### CAPA 1 — DIAGNÓSTICO (Auditable, no opinión)

**Objetivo:** Convertir las respuestas del árbol de 20 preguntas en una evaluación objetiva y auditable del estado actual de la organización frente a gobernanza de IA, cumplimiento legal, riesgos éticos y responsabilidades.

| Output | Fuente que lo sustenta |
|---|---|
| **1.1 Perfil y alcance del sistema de IA:** clasificación de la organización según la bifurcación inicial y delimitación del alcance evaluado. Sin esto, la madurez no es comparable entre empresas. | Bifurcación del flujo |
| **1.2 Inventario de casos de uso de IA:** clasificación de riesgo por caso (alto/medio/bajo según impacto ético y normativo). | Control A.5 de ISO 42001 + función MAP de NIST |
| **1.3 Puntaje de madurez por función NIST AI RMF:** GOVERN, MAP, MEASURE, MANAGE, con desagregación por subcategoría. Permite un radar de madurez visual. | NIST AI RMF |
| **1.4 Cobertura frente a ISO 42001:** análisis de brecha contra cláusulas 4–10 y controles del Anexo A, indicando estado por control (ausente / parcial / implementado). | ISO 42001 |
| **1.5 Registro de brechas priorizado (gap register):** cada brecha con severidad, control afectado, derecho o riesgo comprometido. | NIST + ISO |
| **1.6 Indicador de verificabilidad por respuesta:** distingue entre lo autodeclarado y lo respaldado por evidencia documental, reflejando el nivel de confianza en el diagnóstico. El usuario puede adjuntar documentos propios (fuentes internas) para elevar el nivel de confianza de "autodeclarado" a "verificado con evidencia". Ver sección 6.3 para el flujo de consentimiento y protección de datos al subir archivos. | Concepto propio "verificable" |

### CAPA 2 — RECOMENDACIONES (Hoja de ruta consciente de recursos)

**Objetivo:** Transformar las brechas identificadas en acciones concretas, priorizadas y justificadas, orientadas al cierre de riesgos.

El sistema debe generar recomendaciones asociadas directamente a cada brecha detectada. Cada recomendación debe incluir referencia cruzada con la subcategoría correspondiente del NIST AI RMF y el requisito o control aplicable de ISO/IEC 42001. Ninguna brecha debe generar una recomendación si no existe un control o acción de destino que permita su cierre.

| Output | Descripción |
|---|---|
| **2.1 Recomendación por brecha** | cada una con referencia cruzada a la subcategoría NIST y al control ISO que cierra. Una brecha sin control de destino no genera recomendación. |
| **2.2 Priorización por reducción de riesgo frente vs. esfuerzo/costo** | Matriz o puntaje. Las quick wins de bajo costo tienen el mismo peso que las medidas estructurales. |
| **2.3 Justificación normativa y de derechos** | Por qué importa, qué riesgo o derecho fundamental atiende, y qué requisito del marco satisface. La justificación siempre parte de la Constitución Política del país como fuente primaria de derechos fundamentales, y luego vincula la normativa estatutaria, los controles ISO y las funciones NIST aplicables. |
| **2.4 Esfuerzo estimado y rol responsable sugerido** | Bajo / medio / alto. Define quién ejecuta considerando que una PYME no tiene CISO (ej. dueño, gerente, equipo de TI externo). |
| **2.5 Secuenciación por fases** | 0–30 días, 30–90 días, estructural. |
| **2.6 Criterio de cierre verificable por recomendación** | Qué evidencia concreta demuestra que la brecha quedó cerrada. Cierra el círculo con el indicador de verificabilidad de la Capa 1. |

#### Sobre el plano cartesiano (visualización del output 2.2)

El plano cartesiano es la visualización principal del output 2.2 (priorización). Los ejes dependen de las preguntas formuladas y las respuestas del usuario: no son fijos ni predefinidos, sino que el sistema los determina dinámicamente según el contexto de la PYME, las brechas detectadas y los documentos adjuntos.

**Ejemplos de ejes posibles:** esfuerzo/costo vs. reducción de riesgo · impacto normativo vs. probabilidad de incumplimiento · área afectada vs. consenso requerido. La selección es arbitraria y contextual, no un menú cerrado.

### CAPA 3 — EJECUCIÓN (El SaaS produce, no solo aconseja)

**Objetivo:** Generar los artefactos que cierran las brechas detectadas. La calidad de ejecución que evalúan los jueces se hace tangible aquí.

| Artefacto generado | Fuente / Control |
|---|---|
| **3.1 Políticas generadas con LLM a la medida:** política de IA, uso aceptable, supervisión humana — generadas dinámicamente con LLM a partir del contexto de la organización (país, sector, bifurcación, respuestas del árbol). | ISO 42001 A.2 / cláusula 5.2 |
| **3.2 Registros operativos:** inventario de sistemas de IA, matriz de riesgos, plantilla de evaluación de impacto del sistema de IA. | ISO 42001 A.5 + función MEASURE de NIST |
| **3.3 Procedimientos:** respuesta a incidentes de IA, gobierno de datos, gestión de IA de terceros. | ISO 42001 A.7, A.10 |
| **3.4 Insumos de auditoría:** borrador de Declaración de Aplicabilidad (SoA) de ISO 42001 y lista de verificación con rastro de auditoría. | ISO 42001 (cláusulas 4–10) |
| **3.5 Plan de implementación accionable:** tareas asignables con responsable y fecha, derivadas de la secuenciación de la Capa 2. | Capa 2 output 2.5 |
| **3.6 Constancia verificable:** registro con fecha y referencia de qué se evaluó, qué se encontró y qué se generó. Materialización del adjetivo "verificable". Además, funciona como activo comercial y regulatorio que la PYME puede presentar ante clientes, proveedores o auditorías para demostrar credibilidad en su uso de IA. | Concepto propio |

## MECANISMOS DE SEGURIDAD Y FEEDBACK

### 6.1 Disclaimer obligatorio (siempre visible)

> "Aviso importante: Este sistema tiene fines exclusivamente informativos y de autoevaluación, y no constituye ni reemplaza asesoría legal, regulatoria o profesional especializada. El sistema no solicita información confidencial ni datos sensibles para su funcionamiento. La carga de documentos o evidencias es completamente voluntaria. Al adjuntar cualquier documento, el usuario declara y garantiza que cuenta con las autorizaciones, permisos y derechos necesarios para su tratamiento por parte de la plataforma, así como para compartir dicha información, de conformidad con lo previsto en la Sección 6.3."

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

Este mecanismo refuerza la confianza, permite mejorar el sistema iterativamente y demuestra conciencia de los riesgos de los LLM —alineado con el espíritu del hackathon.

### 6.3 Subida de evidencias y fuentes adicionales por parte del usuario

Para reforzar el indicador de verificabilidad (Capa 1.6), el sistema permite al usuario adjuntar voluntariamente documentos al inicio del flujo (Paso 1), antes de responder el árbol de preguntas. Estos documentos alimentan tanto el diagnóstico como las preguntas que se formularán, ya que el sistema extrae automáticamente la información relevante para validar el cumplimiento ante los controles ISO o funciones NIST correspondientes.

**Flujo:**

1. En el Paso 1 (Contexto), el usuario puede adjuntar documentos (políticas internas, contratos, registros, etc.).
2. Se muestra un checkbox de consentimiento que el usuario debe aceptar antes de subir archivos.
3. El sistema extrae automáticamente la información relevante de los documentos.
4. Los documentos influyen en las preguntas del árbol (Paso 3) y en el nivel de verificabilidad del diagnóstico.
5. La opción de "No adjuntar" siempre está disponible. Si el usuario no adjunta evidencia, el sistema opera con autodeclaración (nivel de confianza: "bajo").

**Declaración de consentimiento (checkbox obligatorio):**

> "Declaro que soy consciente del contenido de los documentos y cuento con los permisos y autorizaciones necesarios para su tratamiento, incluyendo la autorización del titular de datos personales conforme a la normativa aplicable y la Constitución Política de mi país."

**Restricciones técnicas:** PDF, PNG, JPG, DOCX (sin macros) · máximo 5 MB por archivo · los archivos se mantienen solo durante la sesión y la generación del informe.

El texto legal completo del consentimiento (con referencias constitucionales por país) se incluye en el reporte de investigación como consideración de diseño.

## CONTEXTO PARA EL USUARIO (No infraestructura del sistema)

Esta sección proporciona contexto teórico, regulatorio y competitivo para quienes usen o evalúen el sistema. No forma parte de la infraestructura operativa del SaaS.

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
|---|---|---|---|
| Centralidad humana / supervisión humana | Parcial | Sin autoridad clara | Vacío institucional |
| Transparencia, explicabilidad y rendición de cuentas | No | Autorregulación | Vacío normativo |
| Equidad y no discriminación | Parcial | Sin mecanismo de sanción | Vacío de enforceability |
| Privacidad, gobernanza de datos y seguridad | Sí | SIC (Ley 1581/2012) | Cadena completa |
| Robustez, fiabilidad y seguridad | No | Estándares voluntarios | Vacío técnico-normativo |

**Hallazgo clave:** solo el principio de privacidad/datos tiene cadena vinculante completa. Los demás principios carecen de mecanismos de enforceability, lo que justifica la necesidad de un sistema que transforme principios en controles operativos auditables (ISO 42001 + NIST).

> **Nota:** La Ley 1581/2012 regula el tratamiento de datos personales en Colombia, pero la normativa de datos personales NO cubre daños derivados de decisiones automatizadas sin base en datos personales (ej. errores en procesos internos de pymes). Esto amplía el alcance del sistema más allá del cumplimiento estricto de datos.

### 7.3 Diferenciación vs. Herramientas Existentes (fAIr LAC del BID)

Es relevante contextualizar que existen herramientas de autoevaluación ética de IA en la región, como FAIr LAC (3S Ethical AI Self-Assessment, BID Lab). Las diferencias operativas clave de este sistema son:

- fAIr LAC diagnostica y recomienda; este sistema además **PRODUCE** los artefactos que cierran las brechas (Capa 3: políticas generadas con LLM, registros, procedimientos, SoA, constancia verificable).
- **Indicador de verificabilidad:** este sistema distingue lo declarado de lo probado con evidencia documental; fAIr LAC no tiene este mecanismo.
- **Anclaje operativo en ISO 42001 + NIST:** controles concretos y auditables, no solo principios éticos abstractos.
- **Diseño consciente de PYMES:** roles realistas (sin CISO), quick wins, secuenciación por fases, y priorización por esfuerzo/costo.

> **Contexto de evaluación:** dos juezas del hackathon (María Paula Mujica y Mónica Ulloa) tienen afiliación con el BID Lab. Esta diferenciación debe quedar clara en el reporte para evitar que el proyecto sea percibido como redundante con fAIr LAC.

### 7.4 Críticas Esperadas y Respuestas

Para anticipar objeciones de revisores y jueces:

- **"¿Qué aporta vs. herramientas existentes?"** → Generación de artefactos verificables + indicador de verificabilidad + anclaje ISO/NIST operativo.
- **"Esto promueve cumplimiento cosmético."** → El indicador de verificabilidad distingue declarado de probado. El output no es un "sello de aprobado" sino un perfil con acciones pendientes, brechas documentadas y criterios de cierre.
- **"¿Qué pasa después de la evaluación?"** → Las Capas 2 y 3 cierran el ciclo: hoja de ruta priorizada + artefactos generados + plan accionable con fechas y responsables.
- **"Esto puede ser un obstáculo para pymes."** → Priorización por esfuerzo/costo, quick wins de bajo costo, roles sin CISO, y secuenciación por fases (0-30-90 días) hacen el cumplimiento progresivo y viable.

### 7.5 NIST AI RMF Playbook como referencia operativa

El sistema se ancla en el NIST AI Risk Management Framework (AI RMF 1.0) y su Playbook complementario como capa operativa de controles concretos. El Playbook proporciona acciones sugeridas para cada subcategoría de las cuatro funciones, las cuales se resumen a continuación como contexto de diseño:

| Función NIST | Descripción del Playbook | Rol en el sistema |
|---|---|---|
| **GOVERN** | Políticas, procesos, procedimientos y prácticas relacionadas con el mapeo, medición y gestión de riesgos de IA están establecidos, son transparentes e implementados efectivamente. | Capa 1 (madurez por función) + Capa 3 (políticas generadas con LLM, procedimientos) |
| **MAP** | El contexto se establece y se comprende. Casos de uso, usuarios, impactos y supuestos del sistema de IA se documentan. | Capa 1 (inventario de casos de uso, clasificación de riesgo) |
| **MEASURE** | Se identifican y aplican métodos y métricas apropiadas para evaluar riesgos de IA. | Capa 1 (evaluación de impacto, indicadores de verificabilidad) + Capa 3 (plantillas de evaluación) |
| **MANAGE** | Los riesgos de IA se priorizan, responden y gestionan con base en evaluaciones de Map y Measure. | Capa 2 (recomendaciones priorizadas, secuenciación) + Capa 3 (plan de implementación) |

**Relevancia para el diseño:** El Playbook es una guía voluntaria de acciones sugeridas, no un checklist obligatorio. El sistema la utiliza como marco de traducción entre principios éticos (CONPES 4144) y controles operativos concretos que una PYME puede ejecutar. Esto refuerza el anclaje operativo del sistema frente a herramientas que solo diagnostican principios sin accionables.

### 7.6 Hoja de Ruta CIPE/CCIT (2026): Validación regional de la necesidad

El documento "Hoja de ruta para la gobernanza de la IA en el sector privado de América Latina" (CIPE, CCIT, ACTI, COMEX, 2026) valida empíricamente la necesidad que este sistema aborda. Su director es Germán López-Ardila (CCIT), quien además es juez del hackathon.

Propone una **Plataforma Regional del sector privado sobre IA:** un espacio de coordinación bottom-up (no regulatorio) para fortalecer la gobernanza de IA en LATAM, con énfasis en MiPymes. Su plan de acción (12–18 meses) incluye un **Toolkit de IA para MiPymes** (gestión de riesgos, gobernanza de datos, evaluación de impactos), alineado con ISO 42001.

**Alineación con este sistema:**

| Aspecto | Hoja de Ruta CIPE/CCIT | Este sistema (Playbook SaaS) |
|---|---|---|
| Público objetivo | MiPymes del sector privado en LATAM | ✅ Idéntico |
| Necesidad | Falta de herramientas prácticas para MiPymes | ✅ Idéntica |
| Enfoque | Bottom-up, desde empresas | ✅ Idéntico |
| Estándar citado | ISO 42001 | ✅ Idéntico |
| Producto planificado | Toolkit de IA para MiPymes | Playbook SaaS de autodiagnóstico (diseñado) |

**Posicionamiento estratégico:** Este sistema es una implementación operativa concreta del "Toolkit de IA para MiPymes" que la hoja de ruta planifica pero aún no ha construido. Mientras la Plataforma Regional coordina a nivel macro, este sistema entrega el producto a nivel micro (PYME individual). Citar este documento demuestra alineación con el pensamiento de gobernanza regional que el juez Germán López-Ardila lidera, y que el proyecto responde a una agenda regional ya consensuada.

## VALOR / IMPACTO (para la presentación)

- **Impacto social:** democratizar el acceso a la IA responsable.
- **Competitividad:** cumplir abre mercados y reduce riesgo.
- **Contextualización regional (país/sector):** diferenciador frente a frameworks genéricos del Norte Global.
- **Alineado con el objetivo de la hackathon:** traer al Sur Global al centro de la seguridad de la IA.
- **Validación regional documentada:** el sistema responde a una necesidad identificada y consensuada en la Hoja de Ruta CIPE/CCIT (2026) para gobernanza de IA en el sector privado de América Latina, alineándose con el eje de "Desarrollo de capacidades y formación para MiPymes" y con el producto "Toolkit de IA para MiPymes" planificado en esa agenda regional.

## PENDIENTES RESUELTOS Y ABIERTOS

### ✅ Resueltos

| Pendiente | Resolución |
|---|---|
| ¿De dónde sacar la metodología de Evaluación de Impacto? | Control A.5 de ISO 42001 + función MAP de NIST. Plantilla generada en Capa 3 output 3.2. |
| ¿Qué fuente respalda el "mínimo legal"? | Justificación normativa cruzada NIST/ISO en Capa 2 output 2.3 + SoA ISO 42001 en Capa 3 output 3.4. |
| ¿Variables exactas del plano cartesiano? | Arbitrarias: dependen de las preguntas formuladas y las respuestas del usuario. No son fijas ni predefinidas (ver Capa 2). |
| Número de preguntas | Máximo 20. Mantenido como restricción de diseño. |
| ¿Qué pasa con los derechos fundamentales no codificados en leyes ordinarias? | Constitución Política de cada país como fuente obligatoria. Se carga automáticamente según el país seleccionado. |

### ⏳ Aún abiertos (para construir este fin de semana)

| Tarea | Prioridad |
|---|---|
| 1. Diagramar el árbol de preguntas completo (ramas 1/2/3). | ALTA |
| 2. Mapear normativa por país y sector (al menos Colombia para demo). | ALTA |
| 3. Diseñar prototipo visual/mockup del recorrido de las 3 capas. | ALTA |
| 4. Documentar prueba de concepto de un caso recorriendo las 3 capas. | ALTA |
| 5. Preparar reporte PDF de investigación (plantilla Apart). | ALTA |
| 6. Preparar pitch de 3 minutos para showcase domingo 7 PM. | MEDIA |
| 7. Verificar artículo por artículo la Ley 1581 de 2012 (protección de datos personales) como norma vinculante de referencia para el contexto colombiano. | MEDIA |

## RESUMEN EJECUTIVO DE LA ARQUITECTURA

```
┌─────────────────────────────────────────────────────────────┐
│  USUARIO (PYME del Sur Global)                              │
│  Responde árbol de ≤20 preguntas adaptadas                  │
└──────────────────────┬──────────────────────────────────────┘
                     │
    ┌─────────────▼─────────────┐
    │   CAPA 1 — DIAGNÓSTICO    │  ← Auditable, no opinión
    │  • Perfil + inventario    │
    │  • Madurez NIST AI RMF    │
    │    (radar)                │
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

## NOTAS SOBRE EL REPORTE DE ENTREGA (Apart Research)

Para el equipo, recordatorio de la estructura del reporte PDF:

- Plantilla oficial de Apart Research, obligatoria.
- Reporte PDF, ~4 páginas (sin contar referencias/apéndice).
- Reparto sugerido: Intro+Trabajo relacionado 1p, Métodos+Resultados 2.5p, Discusión 0.5p.
- Abstract máx. 150 palabras.
- **Estructura:** Introducción · Trabajo relacionado · Metodología · Resultados · Discusión y limitaciones · Conclusión · Code and Data · Author Contributions · Referencias · Apéndice.
- **Sobre "Code and data":** como el sistema es diseño/mockup (no funcional), esta sección del reporte incluirá el código del prototipo visual (si existe) y/o los datos de la prueba de concepto documentada (caso recorriendo las 3 capas). Si no hay código ejecutable, se explica que es diseño sin implementación funcional.
- **Sección OBLIGATORIA:** "Limitaciones y consideraciones de doble uso".
- **"LLM Usage Statement" obligatorio.**
- Al menos una figura: sugerido radar de madurez NIST y/o diagrama del recorrido de las 3 capas.
- **Idioma:** español permitido sin penalización.
- Evitar texto en cursiva.
- Citas formato libre pero consistente.
- **Entrega:** domingo 21 junio 7:00 PM hora Colombia (hard deadline del hub).
- **Evaluación (1–5 cada una):** impacto/innovación; calidad de ejecución; presentación/claridad.
