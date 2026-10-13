# Estado vigente — 13 de octubre de 2026

Notebook de entrega: `01_notebooks/stock_market_proyecto_organizado.ipynb`.

- Los seis componentes técnicos de la rúbrica están implementados; la matriz detallada está en REVISION_RUBRICA_2026-10-13.md.
- Ejecución completa previamente verificada: 37 celdas, 18 de código. En esta revisión se validó estructura, 18 execution_count presentes y cero errores guardados; no se reentrenó el notebook.
- Se reejecutó `work/verify_v2.py`: PASS en 12×8, exclusión de SPY, invariancia a precios futuros, purga temporal, targets, capital $100,000, benchmark, etiquetas y frontend/demo mediante AppTest.
- Se actualizó el mínimo adicional a **70%** en README, reportes e instrucciones persistentes. En research.py cambió únicamente la frase del reporte, no cálculos, entrenamiento ni selección de modelos. Los originales documentales anteriores están respaldados en la carpeta hermana experimentos/historial_documentacion.
- La asignación original del profesor se conserva literalmente. No se alteraron métricas ni modelos para ajustar el requisito.

## Cumplimiento del mínimo

| Métrica | Resultado máximo original | Comparación con 70% |
|---|---:|---|
| Accuracy de riesgo | 80.6% | Supera 70% |
| Acierto de dirección de retornos | 58.2% | No alcanza 70% |

El usuario no ha definido todavía la métrica/fórmula exacta del mínimo. No se declara cumplido globalmente por comparar porcentajes diferentes. El enunciado original no exige exactitud mínima ni superar el mercado.

## Antes de entregar
El alumno debe revisar, comprender y describir honestamente su propia verificación de IA. La cobertura técnica de la rúbrica no garantiza una nota. La demo es local e histórica; publicar una aplicación no es requisito académico. Los experimentos están separados y no sustituyen el modelo original. El test 2024–2025 ya fue observado; futuros ajustes son exploratorios.
