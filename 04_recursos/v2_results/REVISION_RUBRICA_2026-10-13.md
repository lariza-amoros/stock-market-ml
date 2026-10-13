# Revisión del proyecto — 13 de octubre de 2026

Notebook revisado: stock_market_proyecto_organizado.ipynb (Drive ID 1p8zFZSKyHMsh7hqBYvI9v6a7JMNCpVHg). Enunciado contrastado: ASIGNACION_ORIGINAL.txt. Se mantienen las instrucciones adicionales del profesor y usuario.

## Rúbrica: cobertura de implementación

| Componente | Peso | Verificación |
|---|---:|---|
| Data collection and exploratory analysis | 15% | Ocho acciones de varios sectores; SPY/VIX descargados; enero 2015–diciembre 2025; revisión de nulos/fechas, estadísticas, precios, distribuciones, volatilidad, heatmap y explicación de dificultades |
| Feature engineering and leakage prevention | 15% | Doce variables técnicas por acción: momentum, tendencia, volatilidad, volumen, RSI y MACD; retorno académico a cinco cierres; riesgo con umbral por acción estimado en entrenamiento; purga temporal y pruebas de invariancia |
| Random Forest and XGBoost implementation | 20% | RF/XGBoost para regresión y clasificación, tanto pooled como individuales; dos hiperparámetros por algoritmo |
| Model evaluation and comparison | 20% | MAE, RMSE, directional accuracy, Spearman, accuracy, precision, recall, F1 y ROC-AUC; baselines cero/clase mayoritaria; 96 configuraciones en desarrollo; evaluación comparable; test 2024–2025 |
| Portfolio simulation | 15% | Equal weight, ML top tres y risk-aware ML, más SPY buy-and-hold; $100,000; rebalanceo cinco sesiones y apertura siguiente; costes; métricas completas y figura conjunta |
| Interpretation, conclusions and notebook quality | 15% | Diez características financieras por algoritmo/tarea, comparación entre acciones, siete respuestas en celdas Markdown, cifras y límites explícitos, un notebook autónomo, dependencias/semillas y sección final de IA |

## Decisiones y límites de esta certificación técnica
- SPY/S&P 500 se usa únicamente para EDA/benchmark, según la restricción del profesor. Sus features sugeridas por el enunciado se omiten por esa instrucción adicional; VIX figura en los experimentos de contexto.
- La base de precios comienza el 2 de enero de 2015, primera sesión del año, y termina el 31 de diciembre de 2025. Las filas con características empiezan más tarde por las ventanas de 20 sesiones; no es una descarga incompleta.
- La prueba original usa selecciones fijadas antes de evaluar 2024–2025. Reejecutar parámetros idénticos para comprobar reproducibilidad no constituye un nuevo holdout. Futuras optimizaciones contra ese periodo serían exploratorias.
- El mínimo adicional indicado por el usuario es 70%. La métrica/fórmula no está definida: accuracy de riesgo máximo 80.6% supera ese nivel; acierto de dirección máximo 58.2% no lo alcanza. No confundir accuracy, F1 y rentabilidad ni declarar cumplimiento global del mínimo.
- Las métricas se interpretan por separado: 80.6% es accuracy de riesgo, no F1. La discusión no declara alta capacidad de detección a partir de esa cifra.
- Las ampliaciones macroeconómicas/eventos son complementarias; completar inflación/empleo o publicar una web no es requisito del enunciado base.
- La sección de IA identifica correcciones y contiene comprobaciones ejecutables. El alumno todavía debe entenderlas, reproducirlas personalmente y describir su propia revisión con honestidad.

Esta revisión confirma presencia y funcionamiento de los componentes técnicos; no garantiza una calificación ni sustituye la revisión del profesor o la responsabilidad del alumno.

## Resultado de ejecución
Se ejecutó nuevamente el notebook organizado, de principio a fin, en un entorno limpio: 37 celdas totales y 18 bloques de código, sin errores. Las comprobaciones finales pasaron y las métricas de cartera reprodujeron los resultados originales. No se cambiaron modelos ni hiperparámetros durante esta revisión.
