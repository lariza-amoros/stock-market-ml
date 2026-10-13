# Can Machine Learning Beat the Stock Market?

Proyecto académico de **lariza-amoros**: Random Forest y XGBoost, datos 2015–2025, ocho acciones, pronósticos a cinco sesiones y comparación contra SPY.

- [Notebook completo](01_notebooks/stock_market_proyecto_organizado.ipynb)
- [Informe completo para revisión](04_recursos/v2_results/INFORME_COMPLETO_PROYECTO.md)
- [Métricas originales](04_recursos/v2_results/model_metrics.csv)
- [Carteras originales](04_recursos/v2_results/portfolio_metrics.csv)
- [Frontend](streamlit_app.py)

## Ejecutar localmente

Python **3.12**:

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Los datos y modelos entrenados están incluidos. La app no necesita credenciales ni reentrenamiento para mostrar pronósticos históricos.

## Deploy del frontend

Abrir [Streamlit Community Cloud](https://share.streamlit.io/), iniciar sesión y seleccionar **Create app**:

- Repository: `lariza-amoros/stock-market-ml`
- Branch: `main`
- Main file path: `streamlit_app.py`
- Python: **3.12** en Advanced settings.

Aplicación publicada y probada: [Abrir frontend](https://lariza-stock-market-ml.streamlit.app/). Incluye ocho pronósticos, resultados y cuenta demo histórica.

## Modelo oficial

- Retornos: XGBoost pooled, doce variables técnicas.
- Riesgo: XGBoost individual por acción, doce variables técnicas.
- Entrenamiento anterior a 2024; validación 2023; evaluación conjunta **2024 y 2025**.
- SPY/S&P 500 exclusivamente EDA/benchmark; no entra al entrenamiento.
- Cuenta demo de $100,000, costos 10 bps por lado y ejecución a apertura siguiente.
- Los experimentos posteriores se mantienen separados y no sustituyen el original.

## Resultados y lectura correcta

| Indicador | Resultado |
|---|---:|
| Dirección del modelo oficial | 58.17% |
| Baseline «siempre sube» en la misma muestra | 58.54% |
| Accuracy de riesgo oficial | 77.95% |
| F1 de riesgo oficial | 29.15% |
| Retorno histórico ML top 3 | 126.06% |
| Retorno histórico SPY | 49.68% |

El mínimo adicional actual es **70%**; debe especificarse la métrica. Se supera en accuracy de riesgo, pero no en dirección ni F1. Rentabilidad no equivale a exactitud. El informe explica el balance de clases y por qué «siempre sube» logra un acierto similar o mayor.

## Organización

`01_notebooks/`: entrega autónoma; `02_datos/v2/`: snapshot y contexto; `03_graficos/v2/`: figuras; `04_recursos/v2_results/`: modelos y resultados; `05_codigo/v2/`: pipeline original; `streamlit_app.py`: frontend de entrega.

El notebook incluye seis secciones, interpretaciones, siete preguntas científicas y declaración de IA. La revisión/explicación personal del alumno sigue siendo necesaria. El test ya fue observado; cambios posteriores son exploratorios. Backtesting histórico y demo, sin conexión a bróker, no prueban rendimiento futuro.
