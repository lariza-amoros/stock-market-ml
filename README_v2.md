# Proyecto actualizado — versión v2

## Entregable académico
Usar **01_notebooks/stock_market_proyecto_organizado.ipynb**. Incluye datos reales, todo el código, modelos, experimentos, tablas, figuras, discusión y declaración de uso de IA. Genera sus archivos de trabajo al ejecutarse; no depende de los scripts externos. Los notebooks anteriores se conservan como historial.

## Carpeta actual
- 02_datos/v2: precios reales, calendario de política de la Reserva Federal, catálogo de eventos con fuentes y características por acción.
- 03_graficos/v2: EDA, crecimiento de $100,000 y diez características más importantes para ambos algoritmos/tareas.
- 04_recursos/v2_results: métricas, búsqueda de hiperparámetros, validación temporal, pronósticos, operaciones, modelos, significancia y conclusiones.
- 05_codigo/v2: features.py, models.py, portfolios.py, research.py y app.py. Es la versión que cumple la rúbrica; los scripts previos están conservados y no deben usarse para esta entrega.

## Características
Cada una de las ocho acciones tiene exactamente doce variables técnicas: retornos 1/5/10/20, ratios respecto a medias 5/20, volatilidades 5/20, cambio de volumen, ratio volumen/media20, RSI14 y MACD normalizado. Son 96 combinaciones acción-variable en una tabla longitudinal. Contexto económico y eventos son extensiones separadas, no parte de las doce técnicas.

## Demo account
**Simulador local histórico con $100,000 virtuales.** No requiere bróker, API keys ni cuenta bancaria. Permite elegir fecha fuera de entrenamiento, algoritmo y variables, obtener los ocho pronósticos y simular operaciones a apertura siguiente. Los resultados se revelan usando datos históricos de 2024–2025. El capital se mantiene en la sesión del navegador y puede descargarse como historial CSV. No es una cuenta real de paper trading conectada a mercado en vivo.

Para abrirla, con Python 3.12, entrar en 05_codigo/v2 y ejecutar:

    python -m pip install -r requirements.txt
    python -m streamlit run app.py

El paquete completo incluye los modelos entrenados. Si solo descargas scripts, primero ejecuta research.py con los datos en 02_datos/v2. No se ha publicado en un servicio externo.

## Protocolo
Datos 2015–2025. Selección por validación 2023; entrenamiento final anterior a 2024; prueba 2024–2025. Las etiquetas que cruzan fronteras temporales se excluyen. SPY no entra como predictor, fila de entrenamiento ni target. Las tasas/eventos están disponibles desde la siguiente sesión observada tras su fecha. El catálogo retrospectivo es exploratorio y pequeño; no equivale a estimación causal ni a una base completa de inflación/empleo con publicaciones originales.

## Límites del resultado
El mínimo adicional indicado por el usuario es 70%. La métrica/fórmula no está definida: accuracy de riesgo máximo 80.6% supera ese nivel; acierto de dirección máximo 58.2% no lo alcanza. No confundir accuracy, F1 y rentabilidad ni declarar cumplimiento global del mínimo.
