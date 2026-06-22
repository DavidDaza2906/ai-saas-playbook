# Reporte de evaluación RAG — métricas para el paper
> Generado: 2026-06-21 17:31:48 | k=6 | modelo política: kimi-k2.6 | faithfulness: glm-5.2

## Resumen (agregados)

- **Recall@6 (retrieval):** media 0.85 (min 0.5, max 1.0)
- **Precisión de citas:** 1.0 (100% — cero citas inválidas)
- **Faithfulness (LLM-as-judge):** media 0.883 (min 0.684, max 1.0) sobre n=10
- **Afirmaciones no respaldadas (unfaithful) detectadas:** 13 en total

## Las tres capas de defensa anti-alucinación (modelo de queso suizo de Hendrycks)

1. **Retrieval con umbral** → abstención si no hay fundamento normativo (0 abstenciones en el golden set)
2. **Generación citada + validación determinista** → 100% de citas válidas contra el índice del corpus
3. **Verificador de faithfulness (LLM-as-judge)** → 88.4% de afirmaciones respaldadas por las fuentes

## Detalle por consulta

| ID | Tema | Recall@6 | Prec. citas | Faithfulness | Claims | Faithful | Unfaithful |
|---|---|---|---|---|---|---|---|
| g1 | supervisión humana | 1.0 | 1.0 | 0.833 | 12 | 10 | 1 |
| g2 | datos personales / consentimiento | 0.5 | 1.0 | 0.875 | 16 | 14 | 1 |
| g3 | gobernanza de datos | 0.5 | 1.0 | 0.95 | 20 | 19 | 0 |
| g4 | política de IA | 1.0 | 1.0 | 0.708 | 24 | 17 | 5 |
| g5 | roles y responsabilidades | 1.0 | 1.0 | 1.0 | 18 | 18 | 0 |
| g6 | evaluación de impacto / sesgo | 1.0 | 1.0 | 0.955 | 22 | 21 | 0 |
| g7 | transparencia / comunicación a usuarios | 1.0 | 1.0 | 0.684 | 19 | 13 | 5 |
| g8 | IA de terceros / proveedores | 1.0 | 1.0 | 0.917 | 12 | 11 | 0 |
| g9 | incidentes / respuesta a fallas | 0.5 | 1.0 | 1.0 | 18 | 18 | 0 |
| g10 | beneficencia / impacto positivo | 1.0 | 1.0 | 0.913 | 23 | 21 | 1 |