# Contrato de esquema — Árbol de preguntas (questions.json)

Las preguntas se cargan aquí siguiendo este contrato. El motor (`engine.py`) es
100% data-driven: si cada pregunta cumple este esquema, el sistema funciona sin
modificar código.

> El árbol puede tener **subpreguntas anidadas** (que aparecen según la respuesta
> del padre) y tipos de respuesta variados (opción múltiple, escala Likert,
> número, matriz, texto abierto). Ver secciones específicas más abajo.

## Estructura del archivo
```jsonc
{
  "bifurcacion": { ... },          // Paso 2 (pregunta única que ramifica el árbol)
  "preguntas": [ { ... }, ... ],   // Paso 3 (preguntas base; con o sin subpreguntas)
  "estado_opciones": [ ... ]       // vocabulario de respuesta por defecto
}
```

## Objeto `bifurcacion`
```jsonc
{
  "id": "q0",
  "texto": "...",
  "contexto_pyme": "...",
  "tipo": "single",
  "opciones": [
    { "valor": "1", "etiqueta": "...para productos/servicios a terceros" },
    { "valor": "2", "etiqueta": "...automatizar procesos internos" },
    { "valor": "3", "etiqueta": "Ambas" }
  ]
}
```

## Objeto de cada pregunta
```jsonc
{
  "id": "q1",                       // OBLIGATORIO, único
  "texto": "...",                   // OBLIGATORIO
  "contexto_pyme": "...",           // OBLIGATORIO (lo exige PROPUESTAFINAL §125)
  "tipo": "multiple",               // ver "Tipos de respuesta" abajo
  "ramas": ["1", "2", "3"],         // OBLIGATORIO: en qué bifurcaciones aplica
  "condicion": { "pregunta": "q4", "en": ["implementado","parcial"] },  // OPCIONAL: rama por respuesta previa
  "responsabilidad": "usuario",     // OPCIONAL: proveedor | usuario (split de los 5 principios)
  "pesos": { "etico": 0.0, "iso": 1.0, "nist": 0.8 },  // OPCIONAL: importancia 0..1 por eje (congelados vía RAG). Si falta, se derivan del mapeo (binario).
  "caso_uso": {                     // OPCIONAL: alimenta el inventario (output 1.2) sin IDs cableados
    "caso": "IA que decide sobre personas",
    "riesgo": "alto",               // alto | medio | bajo
    "cuando": ["implementado","parcial"]   // respuestas que activan el caso
  },
  "opciones": [ ... ],              // según el tipo (ver abajo)
  "subpreguntas": [ ... ],          // OPCIONAL: subpreguntas que aparecen según la respuesta de esta pregunta
  "mapeo": {                        // OBLIGATORIO: al menos un nist O un iso (PROPUESTAFINAL §125)
    "nist": ["GOVERN", "MEASURE-2.11"],   // función y/o subcategoría (subcat -> se agrega a su función y se desagrega en 1.3)
    "iso":  ["A.5.2"],              // deben existir en controls.json
    "principio": ["autonomia"]      // 0..n de los 5 principios (eje ético, output 1.2)
  }
}
```

## Tipos de respuesta (`tipo` + `opciones`)

### `multiple` — opción única con valores fijos (modelo principal)
Cada opción lleva un `puntaje` fijo en cualquier escala; el motor normaliza por el máximo.
```jsonc
"tipo": "multiple",
"opciones": [
  { "valor": "a", "etiqueta": "No sé de dónde vienen los datos",   "puntaje": 0 },
  { "valor": "b", "etiqueta": "Sé el origen pero no controlo calidad", "puntaje": 1 },
  { "valor": "c", "etiqueta": "Origen + calidad documentados",      "puntaje": 2 },
  { "valor": "d", "etiqueta": "Origen + calidad + seguridad",       "puntaje": 3 },
  { "valor": "na", "etiqueta": "No aplica",                         "puntaje": null }
]
```

### `multiple_seleccion` — selección múltiple
La respuesta es una **lista** de `valor`. El motor promedia los puntajes de los
seleccionados y luego normaliza.
```jsonc
"tipo": "multiple_seleccion",
"opciones": [ { "valor": "a", "etiqueta": "...", "puntaje": 3 }, ... ]
```

### `likert` — escala 1..N (subtipo de `multiple`)
Igual que `multiple`, pero las opciones representan niveles de una escala. Se
usa igual: `puntaje` por opción (el motor normaliza). Ej. Likert 1-5 con
puntajes 0/0.25/0.5/0.75/1.0.

### `numero` — respuesta numérica con tramos
Para preguntas como "¿cuántos sistemas de IA usa?". El número se discretiza por
**tramos** definidos en la pregunta; cada tramo da un `puntaje`. El tramo puede
activar `condicion`es en preguntas siguientes (ej. tramo "0" salta P4-P7).
```jsonc
"tipo": "numero",
"tramos": [
  { "hasta": 0,            "etiqueta": "Ninguno",                "puntaje": null, "valor_tramo": "0" },
  { "hasta": 3,            "etiqueta": "1 a 3",                  "puntaje": 0.5,  "valor_tramo": "1-3" },
  { "hasta": 999999,       "etiqueta": "4 o más",                "puntaje": 1.0,  "valor_tramo": "4+" },
  { "hasta": null,         "etiqueta": "No sé",                  "puntaje": 0.0,  "valor_tramo": "ns" }
]
```
- La respuesta del usuario es un número (o `"ns"` para "No sé").
- El motor asigna el `valor_tramo` del primer tramo cuyo `hasta` >= respuesta;
  `"ns"` va directo al tramo con `hasta: null`.
- El `valor_tramo` se usa como valor de la pregunta para `condicion`es de otras
  preguntas (ej. `"condicion": { "pregunta": "q3", "en": ["1-3","4+"] }`).

### `matriz` — una entrada por sistema (tabla)
Para preguntas como "clasifique el riesgo de cada sistema". El usuario entrega
una **lista de entradas**, una por sistema declarado en una pregunta `numero`
previa (campo `filas_de`). Cada entrada elige una `opcion`; el motor **agrega**
(por defecto: el peor nivel reportado) y produce el puntaje.
```jsonc
"tipo": "matriz",
"filas_de": "q3",            // ID de la pregunta 'numero' que define cuántas filas
"opciones": [
  { "valor": "bajo",   "etiqueta": "Bajo riesgo",   "puntaje": 1.0 },
  { "valor": "medio",  "etiqueta": "Riesgo medio",  "puntaje": 0.5 },
  { "valor": "alto",   "etiqueta": "Alto riesgo",   "puntaje": 0.0 },
  { "valor": "ns",     "etiqueta": "No sé clasificarlo", "puntaje": 0.0 }
],
"agregacion": "peor"        // peor (default) | promedio
```
- La respuesta es una **lista** de `valor` (uno por fila).
- `"agregacion": "peor"` → toma el menor puntaje (alto riesgo en cualquier
  sistema = bajo puntaje para la pregunta). `"promedio"` → promedia.
- Alimenta el **inventario** (output 1.2): cada fila con `alto`/`medio` se
  registra como caso de uso con su riesgo (sobreescribiendo o sumando al
  `caso_uso` de la pregunta).

### `texto` — texto abierto (no puntúa)
Para capturar narrativa del usuario (ej. justificaciones). **No puntúa**; no
aporta al vector 3D ni al mapeo. Se conserva en la sesión para que el RAG la use
en la Capa 3 (narrativa del diagnóstico, política a la medida).
```jsonc
"tipo": "texto"
```
La respuesta es un string libre. El motor la guarda en
`diag["texto_abierto"][id_pregunta]`.

## Subpreguntas anidadas
Una pregunta puede traer `subpreguntas: [...]`. Cada subpregunta es un objeto
pregunta completo (con su propio `id`, `tipo`, `opciones`, `mapeo`) más una
**`condicion`** que apunta a la respuesta del **padre**:
```jsonc
{
  "id": "q6",
  "texto": "¿Usa datos personales en su IA?",
  "tipo": "multiple",
  "opciones": [ { "valor": "si", "etiqueta": "Sí", "puntaje": 1.0 },
                 { "valor": "no", "etiqueta": "No", "puntaje": 0.0 },
                 { "valor": "ns", "etiqueta": "No sé", "puntaje": 0.0 } ],
  "mapeo": { "nist": ["MAP"], "iso": ["A.6.2"], "principio": ["autonomia"] },
  "subpreguntas": [
    {
      "id": "q6a",
      "texto": "¿Tiene documentado el consentimiento informado?",
      "condicion": { "pregunta": "q6", "en": ["si"] },
      "tipo": "multiple",
      "opciones": [ { "valor": "si", "etiqueta": "Sí", "puntaje": 1.0 },
                     { "valor": "parcial", "etiqueta": "Parcialmente", "puntaje": 0.5 },
                     { "valor": "no", "etiqueta": "No", "puntaje": 0.0 } ],
      "mapeo": { "nist": ["GOVERN"], "iso": ["A.6.2"], "principio": ["autonomia"] }
    }
  ]
}
```
### Reglas de las subpreguntas
- La `condicion` de una subpregunta **siempre** referencia al padre (o a otra
  pregunta previa). La subpregunta se evalúa solo si la condición se cumple.
- La subpregunta **hereda `ramas`** del padre si no define las suyas.
- La subpregunta aporta al vector 3D y al mapeo como cualquier pregunta (con
  sus propios `pesos` o derivados de su `mapeo`).
- Se admiten hasta **2 niveles** de anidamiento (subpreguntas de subpreguntas).
  No más, para mantener el árbol legible.
- Los IDs de subpreguntas deben ser únicos en todo el archivo (como `q6a`).

## Reglas de validación
1. **Tope de preguntas base:** ~20 recomendado (PROPUESTAFINAL §127), pero el
   sistema admite más si el árbol lo requiere. El validador avisa (no bloquea)
   si se supera 20.
2. Cada pregunta (base o subpregunta) **mapea a ≥1 función/subcategoría NIST O
   ≥1 control ISO** (`mapeo.nist` o `mapeo.iso` no vacío). Excepción: las
   `tipo: "texto"` no requieren `mapeo` (no puntúan).
3. Los `iso` deben existir en `controls.json → iso_controls`.
4. Los `principio` deben estar entre: `beneficencia`, `no_maleficencia`,
   `autonomia`, `justicia`, `explicabilidad`.
5. No hay campo `eje`. Los **tres ejes del diagnóstico (ÉTICO, NIST, ISO)** se
   derivan del `mapeo`: una pregunta aporta al eje NIST si trae `mapeo.nist`, al
   eje ISO si trrea `mapeo.iso`, y al eje ÉTICO si trae `mapeo.principio`. Puede
   aportar a los tres a la vez.
6. Las funciones NIST válidas son `GOVERN`, `MAP`, `MEASURE`, `MANAGE`. Las
   subcategorías se escriben `FUNCION-x.y` (ej. `MEASURE-2.11`); el motor deriva
   la función del prefijo.
7. Para cubrir el eje ético completo, entre todas las preguntas (base +
   subpreguntas) debe haber al menos una que mapee a **cada uno** de los 5
   principios (si falta uno, su puntaje saldrá `null`).

## Reglas del scoring (importante)
- Los valores fijos pueden estar en **cualquier escala** (0/1, 0..3, pesos). El
  motor **normaliza** dividiendo por el valor máximo de esa pregunta: en el
  ejemplo, elegir `c` (2 de max 3) da `2/3 = 0.67` de madurez para esa pregunta.
- `puntaje: null` = la opción no puntúa (ej. "No aplica"): no entra en los
  promedios.
- **Opción única** (`multiple`/`likert`): la respuesta es el `valor` elegido.
- **Selección múltiple** (`multiple_seleccion`): la respuesta es una lista de
  `valor`; el motor promedia los seleccionados y luego normaliza.
- **Número** (`numero`): la respuesta es un número o `"ns"`; el motor asigna el
  tramo y su `puntaje`.
- **Matriz** (`matriz`): la respuesta es una lista de `valor` (uno por fila); el
  motor agrega (`peor` o `promedio`) y ese es el puntaje de la pregunta.
- **Texto** (`texto`): no puntúa.
- El `mapeo` (nist/iso/principio) va a nivel de **pregunta**: indica qué control
  evalúa. El `puntaje` de la opción indica **cuánto** lo cumple.

## Vector de diagnóstico: promedio ponderado por eje
El diagnóstico produce un punto en 3D `(x=ÉTICO, y=ISO, z=NIST)`, cada eje 0..100,
calculado como **promedio ponderado** de las respuestas (incluidas las
subpreguntas que se activen):

```
            Σ aᵢ · wᵢ,eje
eje = 100 · ─────────────       aᵢ = puntaje normalizado de la respuesta (0..1)
              Σ wᵢ,eje          wᵢ,eje = peso de la pregunta i en ese eje
```

La suma recorre solo las preguntas **efectivamente puntuadas** (aplicables por
bifurcación/condición, activadas, y no respondidas con "na" o `null`). Por eso
se **normaliza** (divide por Σ pesos): así una PYME que responde menos preguntas
sigue siendo comparable y cada eje queda en escala 0..100.

### De dónde salen los pesos `wᵢ,eje`
- Si la pregunta trae el campo `pesos`, se usan esos valores fijos.
- Si no, se derivan del `mapeo` (binario: 1 si la pregunta toca el eje, 0 si no).

### Cómo se fijan los pesos (una sola vez, reproducible)
1. Se corre `propose_weights.py` (usa el RAG: retrieval normativo + Claude) →
   propone los pesos por eje con justificación, en `data/pesos_propuestos.json`.
2. El equipo los **revisa** y los **congela** en el campo `pesos` de cada
   pregunta.
3. Runtime = pura aritmética determinista: mismas respuestas → mismas
   coordenadas para todas las PYMES. El RAG solo participó en diseño, no en cada
   sesión.

## Vocabulario por defecto (`estado_opciones`)
Si una pregunta es `tipo: "estado"` (legacy) y no define `opciones`, usa este
set (escala 0..1):
```jsonc
[
  { "valor": "implementado", "etiqueta": "Sí, implementado y documentado", "puntaje": 1.0 },
  { "valor": "parcial",      "etiqueta": "Parcialmente / informalmente",   "puntaje": 0.5 },
  { "valor": "ausente",      "etiqueta": "No",                             "puntaje": 0.0 },
  { "valor": "na",           "etiqueta": "No aplica",                      "puntaje": null }
]
```

## Cómo el motor usa cada campo
| Campo | Output que alimenta |
|-------|---------------------|
| `mapeo.nist` | 1.3 madurez por función + subcategoría · Capa 2 ref. NIST |
| `mapeo.iso` | 1.4 cobertura ISO · 1.5 gap register · Capa 2/3 |
| `mapeo.principio` | eje **ÉTICO** del vector · 1.5 principios comprometidos · 2.3 justificación |
| `mapeo.nist` (presencia) | eje **NIST** del vector |
| `mapeo.iso` (presencia) | eje **ISO** del vector |
| `caso_uso` | 1.2 inventario de casos de uso |
| `tipo: matriz` | 1.2 inventario (una entrada por fila con su riesgo) |
| `condicion` | ramas del árbol por respuesta previa (Paso 3) |
| `subpreguntas` | ramas del árbol por respuesta del padre |
| `ramas` | qué preguntas aplican según la bifurcación (Paso 2) |
| `tipo: texto` | narrativa guardada para el RAG (Capa 3), no puntúa |
| respuesta → `puntaje` | todos los puntajes de madurez y estado de control |
