# ÁRBOL DE PREGUNTAS — SaaS de Diagnóstico de Gobernanza de IA para PYMEs

**Playbook de IA Responsable para PYMES | Global South AI Safety Hackathon 2026**

---

## 🎯 ESTRUCTURA DEL ÁRBOL

**Flujo general:** CONTEXTO → BIFURCACIÓN → PREGUNTAS BASE → MÓDULOS ADICIONALES

**Total de preguntas en un recorrido completo:** Máximo 20 (el usuario responde 12-18 dependiendo de su trayectoria)

---

## FASE 0: CONTEXTO / INFRAESTRUCTURA (Paso 1 del Flujo)

### **P0.1 — Ubicación y Sector**

| Atributo | Valor |
|----------|-------|
| **ID** | P0.1 |
| **Pregunta para usuario** | ¿En qué país opera principalmente su organización y a qué sector pertenece? |
| **Contexto adicional** | Esta información carga automáticamente las fuentes normativas vigentes en su jurisdicción: Constitución Política, normativa estatutaria, estándares internacionales (NIST AI RMF, ISO 42001), marcos éticos (UNESCO, OCDE). |
| **Tipo de respuesta** | Selección de país (desplegable) + Sector (menú: Salud, Financiero, Comercio, Manufactura, Educación, Otro). |
| **Ramas activadas** | Toda la normativa posterior se adapta al país seleccionado. |
| **Eje evaluado** | **Gobernanza / Responsabilidad** |
| **Mapeo NIST** | GOVERN (establece el contexto normativo) |
| **Mapeo ISO** | ISO 42001, Cláusula 4 (Contexto de la organización) |
| **Principio ético** | N/A (infraestructura) |
| **Riesgo si omite** | Evaluación sin base normativa específica; recomendaciones genéricas que no aplican al país/sector. |

---

### **P0.2 — Existencia de Políticas o Marcos de IA Previos**

| Atributo | Valor |
|----------|-------|
| **ID** | P0.2 |
| **Pregunta para usuario** | ¿Su organización tiene actualmente políticas, procedimientos o documentación sobre el uso de inteligencia artificial? |
| **Contexto adicional** | Puede ser un documento formal, una guía interna o simplemente normas no escritas. |
| **Tipo de respuesta** | Sí / No / Parcialmente (tenemos algunos documentos pero no completos). |
| **Subpreguntas si responde Sí/Parcialmente** | P0.2a: ¿Puede adjuntar estos documentos para revisar el nivel de cobertura actual? (adjuntar archivo, máximo 5 MB). |
| **Rama activada** | Si Sí/Parcialmente → el sistema extrae información de los documentos y los referencias en el diagnóstico final. Si No → el sistema marca como "Fase 0: Ausencia de marcos documentados". |
| **Eje evaluado** | **Gobernanza / Responsabilidad** |
| **Mapeo NIST** | GOVERN (comunicación e implementación de políticas) |
| **Mapeo ISO** | ISO 42001, Cláusula 5.2 (Políticas) |
| **Principio ético** | Explicabilidad (la documentación evidencia transparencia) |
| **Riesgo si No** | Vacío crítico de gobernanza: no hay base escrita para acciones de IA, riesgo de inconsistencias y falta de responsabilidad asignada. |

---

## FASE 1: BIFURCACIÓN INICIAL (Paso 2 del Flujo)

### **P1 — Tipo de Uso de IA**

| Atributo | Valor |
|----------|-------|
| **ID** | P1 |
| **Pregunta para usuario** | ¿Para qué principalmente utiliza o planea utilizar la inteligencia artificial? Seleccione la opción más cercana a su situación. |
| **Contexto adicional** | Esta bifurcación define qué riesgos legales, éticos y de gobernanza aplican a su organización y qué controles son prioritarios. |
| **Tipo de respuesta** | Selección única (excluyente): |
| | **(A) Desarrollar o mejorar productos/servicios de IA para vender o entregar a clientes/usuarios finales** (ejemplos: chatbot para atención, análisis predictivo para clientes, recomendadores, procesamiento de imágenes) |
| | **(B) Automatizar procesos internos de la organización** (ejemplos: análisis de datos internos, optimización de recursos, automatización de flujos administrativos, reporte automático) |
| | **(C) Ambas A y B** |
| **Rama activada** | **Ruta A (Desarrollo de productos):** activa módulo de Riesgos hacia Terceros (P3, P4, P5). |
| | **Ruta B (Procesos internos):** activa módulo de Riesgos Internos (P6, P7). |
| | **Ruta C (Ambas):** activa TODOS los módulos (P3 a P7). |
| **Eje evaluado** | **Gobernanza / Responsabilidad** |
| **Mapeo NIST** | MAP (mapeo del contexto y alcance del sistema de IA) |
| **Mapeo ISO** | ISO 42001, Cláusula 6.1 (Planificación); Control A.5 (Evaluación de impacto) |
| **Principio ético** | Autonomía (define el grado de control humano requerido); Justicia (determina quién es afectado) |
| **Riesgo si indeciso** | Aplicar controles genéricos sin priorizar riesgos específicos de la organización. |

---

## FASE 2: PREGUNTAS BASE OBLIGATORIAS

**Estas preguntas se hacen SIEMPRE, independientemente de la bifurcación.**

---

### **P2 — Gobernanza General (GOVERN — NIST AI RMF)**

| Atributo | Valor |
|----------|-------|
| **ID** | P2 |
| **Pregunta para usuario** | En su organización, ¿quién tiene responsabilidad clara sobre las decisiones de uso, evaluación y supervisión de sistemas de IA? |
| **Contexto adicional** | Puede ser una persona, un equipo, o una combinación de roles. En una PYME típicamente no existe un CISO dedicado. |
| **Tipo de respuesta** | Selección múltiple (puede marcar más de una): |
| | - (a) Existe un rol dedicado (Oficial de IA, CISO, Gerente de Riesgos, etc.) |
| | - (b) Responsabilidad compartida entre TI, Legal y Operaciones |
| | - (c) Responsabilidad asumida por la Dirección / Gerencia General |
| | - (d) No está claramente asignada |
| | - (e) No sé |
| **Subpreguntas si marca (a)** | P2a: ¿Esa persona/equipo tiene acceso a información sobre políticas normativas, riesgos y mejores prácticas de IA? (Sí / Parcialmente / No) |
| **Rama activada** | Si (d) o (e) → Brecha crítica de gobernanza (GOVERN, Control A.2). |
| **Eje evaluado** | **Gobernanza / Responsabilidad** |
| **Mapeo NIST** | GOVERN (Función 1: políticas, procesos, asignación de responsabilidades) |
| **Mapeo ISO** | ISO 42001, Cláusula 5.1 (Liderazgo y compromiso); Control A.2 (Definición de roles) |
| **Principio ético** | Explicabilidad (define quién responde), Justicia (trazabilidad de decisiones) |
| **Riesgo si Indeciso** | Responsabilidades huérfanas: nadie se hace cargo efectivamente de riesgos de IA; incumplimientos no detectados. |

---

### **P3 — Inventario de Sistemas de IA (MAP — NIST AI RMF)**

| Atributo | Valor |
|----------|-------|
| **ID** | P3 |
| **Pregunta para usuario** | ¿Cuántos sistemas, herramientas o aplicaciones de IA está usando actualmente su organización? (Incluya tanto aplicaciones que desarrollaron internamente como herramientas adquiridas). |
| **Contexto adicional** | IA incluye: chatbots, algoritmos de recomendación, sistemas de clasificación automática, herramientas de procesamiento de lenguaje, análisis predictivo, robótica, etc. No incluya simples automatizaciones sin componente inteligente. |
| **Tipo de respuesta** | Número (campo de texto): ___ sistemas |
| **Subpreguntas si responde > 0** | P3a: ¿Puede adjuntar un listado de estos sistemas (nombre, función, tipo de datos que procesa, fecha de implementación)? (campo de texto o adjuntar archivo CSV/XLSX). |
| | P3b: Para cada sistema principal, ¿sabe usted o alguien en su organización cómo toma decisiones el sistema de IA? (Sí para todos / Sí para algunos / No / No sé). |
| **Rama activada** | Si 0 → salta a siguiente módulo (empresa sin IA aún). Si > 0 → continúa con clasificación de riesgo (P4). |
| **Eje evaluado** | **Gobernanza / Responsabilidad**, **Ético** (impacto en personas) |
| **Mapeo NIST** | MAP (mapear los sistemas de IA, sus contextos, usuarios y supuestos) |
| **Mapeo ISO** | ISO 42001, Control A.5 (Evaluación de impacto del sistema de IA) |
| **Principio ético** | Explicabilidad (conocimiento del sistema), Autonomía (control sobre decisiones) |
| **Riesgo si No Sabe** | Sistemas de IA operando sin supervisión; descubrimiento tardío de problemas; falta de documentación para auditoría. |

---

### **P4 — Clasificación de Riesgo por Caso de Uso (MAP/MEASURE — NIST AI RMF)**

| Atributo | Valor |
|----------|-------|
| **ID** | P4 |
| **Pregunta para usuario** | Para cada sistema de IA identificado en P3, clasifique el nivel de riesgo según el impacto en personas y derechos. Si tiene múltiples sistemas, marque todos los que apliquen. |
| **Contexto adicional** | "Alto riesgo" significa que un fallo o sesgo del sistema podría afectar derechos fundamentales (libertad, igualdad, dignidad) o generar daños graves. |
| **Tipo de respuesta** | Matriz (para cada sistema mencionado en P3): |
| | Sistema: _____ |
| | [ ] (A) Bajo riesgo: Decisiones informativas o de bajo impacto (ej. recomendaciones, reportes) |
| | [ ] (B) Riesgo medio: Afecta procesos de negocios internos o decisiones que impactan empleados/clientes moderadamente (ej. asignación de tareas, análisis de crédito inicial) |
| | [ ] (C) Alto riesgo: Determina acceso a derechos/servicios fundamentales o afecta significativamente a personas (ej. aprobación/rechazo de crédito final, diagnóstico médico, evaluación de desempeño laboral que afecta empleo) |
| | [ ] (D) No sé clasificarlo |
| **Rama activada** | Si (C) en cualquier sistema → Módulo de Control de Riesgos Altos (P5). |
| | Si (B) en cualquier sistema → se activan controles medianos (incluido en Capa 2 de recomendaciones). |
| **Eje evaluado** | **Ético** (impacto en derechos), **Legal** (vulnerabilidad de cumplimiento) |
| **Mapeo NIST** | MAP (entender el contexto e impacto) + MEASURE (evaluar riesgos) |
| **Mapeo ISO** | ISO 42001, Control A.5.1 (Evaluación de impacto del sistema de IA) |
| **Principio ético** | No maleficencia (identificar daños potenciales), Justicia (equidad en decisiones) |
| **Riesgo si mal clasificado** | Subestimar riesgos altos lleva a controles insuficientes; sobrestimar genera carga operativa innecesaria. |

---

### **P5 — Transparencia y Documentación (GOVERN/MEASURE — NIST AI RMF)**

| Atributo | Valor |
|----------|-------|
| **ID** | P5 |
| **Pregunta para usuario** | ¿Existen documentos que describan cómo funciona cada sistema de IA que usa? Incluya especificaciones técnicas, diccionarios de datos, decisiones de diseño, limitaciones conocidas. |
| **Contexto adicional** | Esta documentación es clave para auditoría, cumplimiento y mejora continua. |
| **Tipo de respuesta** | Escala de Likert (1-5): |
| | 1 = No existe documentación |
| | 2 = Existe documentación muy limitada (parcial o desactualizada) |
| | 3 = Existe documentación básica pero con vacíos |
| | 4 = Existe documentación completa pero requiere actualización |
| | 5 = Existe documentación completa y actualizada regularmente |
| **Subpreguntas si responde 1-3** | P5a: ¿Tiene acceso a la documentación del proveedor de la herramienta de IA? (Sí / Parcialmente / No). |
| | P5b: ¿Sabe qué datos internos se están usando para entrenar o alimentar estos sistemas? (Sí / Parcialmente / No). |
| **Rama activada** | Si (1) → brecha crítica de explicabilidad y MEASURE (NIST). Si (2-3) → brecha a documentar. Si (4-5) → fortaleza a mantener. |
| **Eje evaluado** | **Gobernanza / Responsabilidad**, **Ético** (explicabilidad) |
| **Mapeo NIST** | MEASURE (métodos y métricas para evaluar riesgos) + GOVERN (documentación de políticas) |
| **Mapeo ISO** | ISO 42001, Control A.7.2 (Documentación del sistema de IA) |
| **Principio ético** | Explicabilidad (inteligibilidad), Autonomía (capacidad de cuestionar decisiones) |
| **Riesgo si 1-2** | Imposibilidad de auditar cumplimiento normativo; decisiones de IA no trazables; imposible detectar sesgos o errores. |

---

### **P6 — Datos Personales (GOVERN/MAP — NIST AI RMF; Ley 1581/2012 en Colombia)**

| Atributo | Valor |
|----------|-------|
| **ID** | P6 |
| **Pregunta para usuario** | ¿Su organización está utilizando datos personales (ej. nombre, email, género, edad, datos de desempeño laboral, historial de crédito, información médica, ubicación, hábitos de compra) en cualquiera de sus sistemas de IA? |
| **Contexto adicional** | Aplica a cualquier información que pueda identificar directa o indirectamente a una persona física. Es obligatorio bajo la Ley 1581/2012 (Colombia) y legislación equivalente en otros países. |
| **Tipo de respuesta** | Sí / No / No sé |
| **Subpreguntas si responde Sí** | P6a: ¿Tiene documentado el consentimiento informado de las personas cuyos datos está utilizando? (Sí / Parcialmente / No). |
| | P6b: ¿Ha realizado una evaluación de impacto en privacidad (DPIA o equivalente) antes de usar esos datos? (Sí / No / No sé qué es). |
| | P6c: ¿Existe un Responsable de Protección de Datos o alguien designado para atender derechos de acceso, rectificación y eliminación de datos? (Sí / No / No aplica). |
| **Rama activada** | Si Sí → Módulo de Cumplimiento de Privacidad (obligatorio). Si No → continúa normalmente pero P6c se descarta. |
| **Eje evaluado** | **Legal** (cumplimiento normativo de privacidad), **Ético** (Autonomía sobre datos personales) |
| **Mapeo NIST** | MAP (identificar datos utilizados) + GOVERN (consentimiento y políticas) |
| **Mapeo ISO** | ISO 42001, Control A.6 (Gestión de datos del sistema de IA); Cláusula 9 (Privacidad y seguridad de datos) |
| **Principio ético** | Autonomía (consentimiento informado), Justicia (equidad en tratamiento de datos) |
| **Riesgo si No Documentado** | Incumplimiento de Ley 1581/2012 (Colombia) y legislación equivalente; multas regulatorias; demandas de titulares de datos; pérdida de confianza. |

---

### **P7 — Supervisión Humana en Decisiones Críticas (MANAGE — NIST AI RMF)**

| Atributo | Valor |
|----------|-------|
| **ID** | P7 |
| **Pregunta para usuario** | Para los sistemas de IA clasificados como "alto riesgo" o "riesgo medio" en P4, ¿existe un paso de revisión o aprobación humana ANTES de que el sistema tome la decisión final? |
| **Contexto adicional** | En sistemas críticos (aprobación de crédito, diagnóstico médico, decisiones laborales), la supervisión humana es obligatoria bajo NIST AI RMF y recomendaciones de UNESCO. |
| **Tipo de respuesta** | Selección múltiple (para cada sistema crítico): |
| | [ ] (A) Sí, existe revisión humana obligatoria en TODAS las decisiones |
| | [ ] (B) Sí, existe revisión humana solo en algunos casos (ej. cuando el sistema marca una alerta o tiene confianza baja) |
| | [ ] (C) No, el sistema toma decisiones de forma completamente automática |
| | [ ] (D) No sé |
| **Subpreguntas si responde C** | P7a: ¿Quién es responsable de monitorear errores o problemas con ese sistema? |
| | P7b: ¿Con qué frecuencia se revisa el desempeño del sistema? (Diariamente / Semanalmente / Mensualmente / Anualmente / Nunca). |
| **Rama activada** | Si (C) en sistema de alto riesgo → Brecha crítica de control (MANAGE, GOVERN). |
| **Eje evaluado** | **Gobernanza / Responsabilidad**, **Ético** (Autonomía humana) |
| **Mapeo NIST** | MANAGE (supervisión y respuesta a riesgos identificados) |
| **Mapeo ISO** | ISO 42001, Control A.8 (Supervisión operativa) |
| **Principio ético** | Autonomía (control humano sobre decisiones que afectan personas) |
| **Riesgo si C** | Decisiones automatizadas sin capacidad de corrección humana; imposibilidad de responsabilizar a personas; falta de adaptación a casos excepcionales. |

---

## FASE 3: MÓDULOS ADICIONALES (Activados según Bifurcación)

---

## MÓDULO A: RIESGOS HACIA TERCEROS (Activado si Ruta A o C en P1)

### **P8A — Comunicación de Riesgos a Usuarios Finales (GOVERN/MEASURE — NIST AI RMF)**

| Atributo | Valor |
|----------|-------|
| **ID** | P8A |
| **Pregunta para usuario** | Si su producto/servicio utiliza IA, ¿comunica clara y anticipadamente a los clientes/usuarios finales que está utilizando sistemas de inteligencia artificial, qué hace ese sistema, y cuál es el riesgo de error? |
| **Contexto adicional** | Esto es parte del principio de Autonomía: las personas afectadas tienen derecho a saber y cuestionar decisiones que las impactan. |
| **Tipo de respuesta** | Escala (1-5): |
| | 1 = No se comunica nada sobre IA |
| | 2 = Se menciona brevemente en términos confusos |
| | 3 = Se explica que existe IA pero sin detalles técnicos |
| | 4 = Se explica la IA, su función y limitaciones de forma clara |
| | 5 = Se ofrece transparencia total + opción de no usar IA o de intervención humana |
| **Subpreguntas si 1-2** | P8a: ¿Por qué no comunica? (Complejidad técnica / Temor a perder clientes / No lo vemos necesario / Otro). |
| **Rama activada** | Si (1-2) → Brecha de Explicabilidad y Autonomía (NIST GOVERN). |
| **Eje evaluado** | **Ético** (Explicabilidad, Autonomía), **Legal** (transparencia exigida por ley en muchos contextos) |
| **Mapeo NIST** | GOVERN (comunicación clara de riesgos y decisiones sobre IA) |
| **Mapeo ISO** | ISO 42001, Cláusula 5.4 (Comunicación sobre sistemas de IA) |
| **Principio ético** | Explicabilidad, Autonomía (consentimiento informado) |
| **Riesgo si 1** | Incumplimiento de normativa de transparencia (ej. EU AI Act); desconfianza de clientes si descubren que está usando IA sin avisar; demandas legales. |

---

### **P8B — Evaluación de Impacto Diferenciado (MEASURE — NIST AI RMF)**

| Atributo | Valor |
|----------|-------|
| **ID** | P8B |
| **Pregunta para usuario** | Para cada grupo de usuarios de su producto, ¿ha evaluado si el sistema de IA funciona de manera equivalente o si muestra sesgos? Por ejemplo: ¿el sistema funciona igual de bien para hombres y mujeres, para diferentes grupos étnicos, edades, niveles de ingresos? |
| **Contexto adicional** | Los algoritmos de IA frecuentemente presentan sesgos no intencionales. Detectarlos es parte del cumplimiento de No Maleficencia y Justicia. |
| **Tipo de respuesta** | Selección múltiple (para cada caso de uso de producto): |
| | [ ] (A) Sí, realizamos auditorías regulares de sesgo y equidad |
| | [ ] (B) Sí, lo hicimos una vez antes de lanzar pero no de forma continua |
| | [ ] (C) No lo hemos hecho pero sabemos que debería hacerlo |
| | [ ] (D) No lo hemos hecho y no vemos por qué sea necesario |
| | [ ] (E) No sé cómo evaluar esto |
| **Subpreguntas si responde B-E** | P8b: ¿Tiene acceso a herramientas o servicios de auditoría de sesgo/fairness? (Sí / No / No sé). |
| **Rama activada** | Si (D) → brecha de No Maleficencia (desatención de discriminación potencial). Si (C-E) → brecha a documentar con plan de mejora. |
| **Eje evaluado** | **Ético** (Justicia, No maleficencia) |
| **Mapeo NIST** | MEASURE (evaluar el comportamiento del sistema en diferentes contextos) |
| **Mapeo ISO** | ISO 42001, Control A.5.3 (Evaluación de sesgo y equidad) |
| **Principio ético** | Justicia (no discriminación), No maleficencia (prevenir daños dirigidos a grupos vulnerables) |
| **Riesgo si D** | Discriminación no detectada; exposición a demandas por violación de derechos; daño reputacional; incumplimiento de leyes anti-discriminación. |

---

## MÓDULO B: RIESGOS INTERNOS (Activado si Ruta B o C en P1)

### **P9B — Datos de Empleados o Información Sensible Interna (GOVERN/MAP — NIST AI RMF)**

| Atributo | Valor |
|----------|-------|
| **ID** | P9B |
| **Pregunta para usuario** | ¿Está utilizando sistemas de IA para procesar información sobre empleados (evaluación de desempeño, asignación de tareas, análisis de comportamiento) u otra información sensible de la organización (financiera, comercial, intelectual)? |
| **Contexto adicional** | Esta información requiere controles específicos bajo normas de seguridad, privacidad y cumplimiento. |
| **Tipo de respuesta** | Sí / No / Parcialmente |
| **Subpreguntas si responde Sí/Parcialmente** | P9a: ¿Han sido informados los empleados/partes interesadas que sus datos están siendo procesados por IA? (Sí / Parcialmente / No). |
| | P9b: ¿Existe documentación sobre qué datos se están usando y con qué propósito? (Sí / Parcialmente / No). |
| **Rama activada** | Si Sí → verificar Privacidad e impacto en relaciones laborales. |
| **Eje evaluado** | **Gobernanza / Responsabilidad**, **Legal** (protección de derechos de empleados) |
| **Mapeo NIST** | MAP (identificar qué datos se usan) + GOVERN (políticas sobre datos internos) |
| **Mapeo ISO** | ISO 42001, Cláusula 9 (Privacidad y seguridad); Control A.6 (Gestión de datos) |
| **Principio ético** | Autonomía (empleados tienen derecho a saber), Justicia (trato equitativo) |
| **Riesgo si No Documentado** | Incumplimiento de normas laborales; vulneración de privacidad de empleados; conflictos laborales; violación de derecho a la información. |

---

### **P10B — Continuidad Operativa y Falla del Sistema de IA (MEASURE/MANAGE — NIST AI RMF)**

| Atributo | Valor |
|----------|-------|
| **ID** | P10B |
| **Pregunta para usuario** | Si uno de sus sistemas de IA fallara o diera resultados incorrectos, ¿cuál sería el impacto en la operación de su organización? ¿Podría continuar operando manualmente o dependería completamente del sistema? |
| **Contexto adicional** | Esto evalúa la resiliencia operativa y el nivel de dependencia de IA. |
| **Tipo de respuesta** | Escala (1-5): |
| | 1 = Dependencia total: sin IA no podemos operar |
| | 2 = Dependencia alta: tendríamos grandes dificultades sin IA |
| | 3 = Dependencia media: podría continuar pero con impacto significativo |
| | 4 = Baja dependencia: podría continuar normalmente (IA es un suplemento) |
| | 5 = No dependencia: IA es solo experimental o muy marginal |
| **Subpreguntas si responde 1-2** | P10a: ¿Existe un plan de contingencia si el sistema falla? (Sí / Parcialmente / No). |
| | P10b: ¿Quién monitorea el desempeño del sistema para detectar fallos? |
| **Rama activada** | Si (1) sin plan → brecha crítica de MANAGE (gestión de riesgos). |
| **Eje evaluado** | **Gobernanza / Responsabilidad** (continuidad del negocio) |
| **Mapeo NIST** | MANAGE (respuesta y recuperación ante riesgos identificados) |
| **Mapeo ISO** | ISO 42001, Cláusula 8.3 (Control operativo); Control A.8.2 (Monitoreo del desempeño) |
| **Principio ético** | Beneficencia (servicio confiable a usuarios internos) |
| **Riesgo si 1 sin plan** | Paralización operativa si sistema falla; incapacidad de servir a clientes; reputación dañada; exposición a incumplimientos contractuales. |

---

## FASE 4: PREGUNTAS FINALES DE SÍNTESIS

### **P11 — Cambios o Evolución en Sistemas de IA (MANAGE — NIST AI RMF)**

| Atributo | Valor |
|----------|-------|
| **ID** | P11 |
| **Pregunta para usuario** | ¿Ha realizado cambios significativos a sistemas de IA existentes (actualizaciones, re-entrenamiento, cambios en datos, cambios en criterios de decisión) en los últimos 12 meses? |
| **Contexto adicional** | Los cambios en IA pueden introducir nuevos riesgos (sesgos, degradación de precisión, impactos no anticipados). |
| **Tipo de respuesta** | Sí / No / No aplica |
| **Subpreguntas si responde Sí** | P11a: ¿Se re-evaluaron los riesgos después de cada cambio? (Sí / Parcialmente / No). |
| | P11b: ¿Fue comunicado a usuarios/clientes/empleados que hubo cambios? (Sí / Parcialmente / No / No era necesario). |
| **Rama activada** | Si Sí sin re-evaluación → brecha de MEASURE (no evaluar continuamente). |
| **Eje evaluado** | **Gobernanza / Responsabilidad** (adaptación continua) |
| **Mapeo NIST** | MANAGE (monitoreo y mejora continua) |
| **Mapeo ISO** | ISO 42001, Cláusula 8.5 (Control de cambios) |
| **Principio ético** | Explicabilidad (transparencia sobre cambios), No maleficencia (anticipar nuevos riesgos) |
| **Riesgo si Sin re-evaluación** | Introducción de nuevos sesgos; regresión de desempeño; comunicación tardía de cambios que afectan a usuarios. |

---

### **P12 — Incidentes o Quejas Relacionadas con IA (MANAGE — NIST AI RMF)**

| Atributo | Valor |
|----------|-------|
| **ID** | P12 |
| **Pregunta para usuario** | ¿Ha experimentado algún incidente, queja o problema con un sistema de IA que haya impactado negativamente a clientes, empleados o la organización? (Ej. discriminación detectada, error de clasificación grave, seguridad comprometida, rechazo infundado de usuario, falta de transparencia detectada). |
| **Contexto adicional** | Documentar incidentes es crucial para mejorar controles y demostrar diligencia debida. |
| **Tipo de respuesta** | Sí / No / No sé |
| **Subpreguntas si responde Sí** | P12a: ¿Fue documentado y investigado? (Sí / Parcialmente / No). |
| | P12b: ¿Se tomaron acciones correctivas? (Sí / Parcialmente / No). |
| | P12c: ¿Puede adjuntar un resumen del incidente y su resolución? (campo de texto o documento). |
| **Rama activada** | Si Sí sin documentación → brecha de MEASURE/MANAGE. Adjuntos se integran en el diagnóstico final. |
| **Eje evaluado** | **Gobernanza / Responsabilidad** (capacidad de respuesta) |
| **Mapeo NIST** | MANAGE (identificar, reportar y responder a problemas) |
| **Mapeo ISO** | ISO 42001, Control A.10 (Gestión de incidentes de IA) |
| **Principio ético** | Explicabilidad (aprender de errores), No maleficencia (prevención iterativa) |
| **Riesgo si No Documentado** | Repetición de problemas; falta de evidencia de diligencia ante demandas; mejora continua obstaculizada. |

---

## FASE 5: DIAGNÓSTICO Y FEEDBACK FINAL

### **P13 — Autoevaluación de Madurez (Síntesis)**

| Atributo | Valor |
|----------|-------|
| **ID** | P13 |
| **Pregunta para usuario** | En una escala de 1 a 5, ¿cuál es su evaluación personal del nivel de gobernanza, cumplimiento normativo y supervisión ética que su organización tiene sobre los sistemas de IA que usa? |
| **Contexto adicional** | Esta pregunta no sustituye la evaluación del sistema, pero captura la percepción del usuario para comparación y validación. |
| **Tipo de respuesta** | Escala Likert (1-5) + campo de texto abierto (¿por qué elegiría este puntaje?). |
| **Rama activada** | Si la auto-evaluación es significativamente diferente de la evaluación del sistema → señal de brecha en conciencia o precisión. |
| **Eje evaluado** | **Gobernanza / Responsabilidad** (conciencia organizacional) |
| **Mapeo NIST** | GOVERN (capacidad y compromiso organizacional) |
| **Mapeo ISO** | N/A (meta-evaluación) |
| **Principio ético** | Reflexión (mejora continua) |
| **Riesgo si Brecha Grande** | Falta de conciencia sobre debilidades; resistencia a cambios; implementación superficial de recomendaciones. |

---

---

## 📊 MATRIZ DE MAPEO: PREGUNTAS → FUNCIONES NIST → PRINCIPIOS ÉTICOS

| Pregunta | NIST GOVERN | NIST MAP | NIST MEASURE | NIST MANAGE | Beneficencia | No Maleficencia | Autonomía | Justicia | Explicabilidad |
|----------|-------------|----------|--------------|------------|--------------|-----------------|-----------|---------|----------------|
| **P0.1** Ubicación/Sector | ✓ | | | | | | | | |
| **P0.2** Políticas previas | ✓ | | | | | | | | ✓ |
| **P1** Bifurcación (tipo de uso) | ✓ | ✓ | | | | | ✓ | ✓ | |
| **P2** Gobernanza general | ✓ | | | | | | | ✓ | ✓ |
| **P3** Inventario de IA | | ✓ | | | | | | | ✓ |
| **P4** Clasificación de riesgo | | ✓ | ✓ | | | ✓ | | ✓ | |
| **P5** Transparencia y doc. | ✓ | | ✓ | | | | ✓ | | ✓ |
| **P6** Datos personales | ✓ | ✓ | | | | | ✓ | ✓ | |
| **P7** Supervisión humana | ✓ | | | ✓ | | ✓ | ✓ | | |
| **P8A** Comunicación a usuarios | ✓ | | ✓ | | | | ✓ | | ✓ |
| **P8B** Evaluación de sesgo | | ✓ | ✓ | | | ✓ | | ✓ | |
| **P9B** Datos de empleados | ✓ | ✓ | | | | | ✓ | ✓ | |
| **P10B** Continuidad operativa | | | ✓ | ✓ | ✓ | | | | |
| **P11** Cambios en sistemas | | | | ✓ | | ✓ | | | ✓ |
| **P12** Incidentes | | | ✓ | ✓ | | ✓ | | | ✓ |
| **P13** Auto-evaluación | ✓ | | | | | | | | |

---

---

## 📋 MATRIZ DE MAPEO: PREGUNTAS → ISO/IEC 42001 CONTROLES

| Pregunta | Cláusula ISO | Control A (ISO) | Descripción del Control |
|----------|-------------|-----------------|------------------------|
| **P0.1** | Cláusula 4 | | Contexto de la organización |
| **P0.2** | Cláusula 5.2 | A.2 | Políticas de IA |
| **P1** | Cláusula 6.1 | A.5 | Evaluación de impacto |
| **P2** | Cláusula 5.1 | A.2 | Liderazgo y roles |
| **P3** | Cláusula 6.1 | A.5 | Inventario de sistemas |
| **P4** | Cláusula 6.1 | A.5.1 | Evaluación de impacto |
| **P5** | Cláusula 8.1 | A.7.2 | Documentación del sistema |
| **P6** | Cláusula 9 | A.6 | Gestión de datos |
| **P7** | Cláusula 8 | A.8 | Supervisión operativa |
| **P8A** | Cláusula 5.4 | A.5.4 | Comunicación sobre IA |
| **P8B** | Cláusula 8 | A.5.3 | Sesgo y equidad |
| **P9B** | Cláusula 9 | A.6 | Datos internos |
| **P10B** | Cláusula 8.3 | A.8.2 | Control operativo |
| **P11** | Cláusula 8.5 | A.8.5 | Control de cambios |
| **P12** | Cláusula 8 | A.10 | Gestión de incidentes |
| **P13** | Cláusula 5.1 | | Auto-evaluación |

---

---

## 🎯 RECORRIDOS TÍPICOS (Número de preguntas por ruta)

### **Ruta A: Desarrollo de Productos con IA (Máx. 18 preguntas)**
P0.1 → P0.2 → P1(A) → P2 → P3 → P4 → P5 → P6 → P7 → P8A → P8B → P11 → P12 → P13 = **14 preguntas base + dinámicas en P3, P4, P8**

### **Ruta B: Automatización de Procesos Internos (Máx. 16 preguntas)**
P0.1 → P0.2 → P1(B) → P2 → P3 → P4 → P5 → P6 → P7 → P9B → P10B → P11 → P12 → P13 = **14 preguntas base + dinámicas en P3, P4**

### **Ruta C: Ambas (Máx. 20 preguntas)**
P0.1 → P0.2 → P1(C) → P2 → P3 → P4 → P5 → P6 → P7 → P8A → P8B → P9B → P10B → P11 → P12 → P13 = **16 preguntas + dinámicas en P3, P4, P8**

---

---

## 📌 NOTAS DE IMPLEMENTACIÓN

### **Criterios de Ramificación**

1. **P0.1 (País/Sector):** Activa marcos normativos específicos en backend.
2. **P1 (Bifurcación):** Determina ruta principal (A, B, o C).
3. **P3 (Inventario):** Si 0 sistemas → salta directamente a cierre del diagnóstico. Si > 0 → continúa.
4. **P4 (Riesgo Alto):** Si clasifica "Alto riesgo" → activa P8B (evaluación de sesgo) con prioridad.
5. **P6 (Datos Personales):** Si Sí → exige P6a y P6b. Si No → salta P6c.

### **Niveles de Verificabilidad (por tipo de respuesta)**

- **Respuesta sin evidencia adjunta:** Nivel bajo de verificabilidad ("Autodeclaración")
- **Respuesta con documento adjunto (política, evaluación, incidente):** Nivel medio ("Parcialmente verificado")
- **Respuesta con múltiples documentos actualizados y trazables:** Nivel alto ("Verificado con evidencia")

### **Indicadores de Riesgo por Pregunta**

Cada pregunta tiene umbrales que activan **brechas prioritarias**:

- **P2:** Si (d) o (e) → Brecha CRÍTICA (Gobernanza huérfana)
- **P5:** Si (1) → Brecha CRÍTICA (Imposibilidad de auditar)
- **P7:** Si (C) en alto riesgo → Brecha CRÍTICA (Automatización sin supervisión)
- **P6:** Si Sí sin P6a → Brecha ALTA (Violación de consentimiento)
- **P8B:** Si (D) → Brecha ALTA (Discriminación potencial no evaluada)

---

## 🔄 FLUJO DE SÍNTESIS (Capa 1 → Outputs)

Cada respuesta alimenta:

1. **CAPA 1 — DIAGNÓSTICO:**
   - 1.1 (Perfil): P0.1, P1
   - 1.2 (Inventario): P3, P4
   - 1.3 (Madurez NIST): Puntuación de P2-P12 mapeada a funciones NIST
   - 1.4 (Brechas ISO): Mapeo de respuestas insuficientes a controles ISO faltantes
   - 1.5 (Gap Register): Brechas priorizado por severidad
   - 1.6 (Verificabilidad): Nivel según evidencia adjunta en P0.2, P3a, P6c, P12c

2. **CAPA 2 — RECOMENDACIONES:**
   - Generadas dinámicamente para cada brecha identificada
   - Priorizadas por riesgo/esfuerzo (plano cartesiano con ejes definidos por P4)

3. **CAPA 3 — EJECUCIÓN:**
   - Políticas generadas según país (P0.1), sector, tipo de uso (P1)
   - Registros basados en inventario (P3) y datos (P6)
   - Procedimientos según brechas identificadas

---

## ✅ VALIDACIÓN DEL ÁRBOL

- **Cobertura NIST:** Cada función (GOVERN, MAP, MEASURE, MANAGE) aparece en al menos 3 preguntas.
- **Cobertura ética:** Cada principio (Beneficencia, No maleficencia, Autonomía, Justicia, Explicabilidad) aparece en al menos 2 preguntas.
- **Cobertura ISO:** Cláusulas 4-10 cubiertas; Controles A.2, A.5, A.6, A.7, A.8, A.10 reflejados.
- **Máximo 20 preguntas:** El recorrido más largo es 16 preguntas base + dinámicas (< 20).
- **Lenguaje accesible:** Todas las preguntas evitan jerga técnica; incluyen contexto PYME.
- **Evidencia verificable:** Cada pregunta tiene opciones de adjuntar documentos o proporcionar detalles verificables.

---

## 🚀 PRÓXIMOS PASOS

1. **Implementar sistema dinámico** que ramifique según respuestas (arquitectura de decisión en backend).
2. **Crear banco de preguntas adicionales** por sector (Salud, Financiero, E-commerce, Manufactura, Educación).
3. **Desarrollar plantillas de evaluación** (DPIA, auditoría de sesgo, evaluación de impacto) para P4, P8B, P12.
4. **Diseñar recomendaciones dinámicas** que mapen cada brecha a acciones concretas con cronograma.
5. **Validar con PYMES piloto** antes de lanzamiento (prueba de concepto).
