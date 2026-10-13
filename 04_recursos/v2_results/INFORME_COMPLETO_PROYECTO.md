# Informe completo para revisión del proyecto
## Can Machine Learning Beat the Stock Market?

**Fecha:** 13 de octubre de 2026. **Autora/cuenta de entrega:** lariza-amoros. **Versión:** modelo original v2 y notebook organizado. Este informe sirve para revisar código y resultados; no cambia los modelos ni incorpora experimentos posteriores.

## 1. Estado ejecutivo
El entregable académico está implementado y se ejecutó de principio a fin. El notebook vigente tiene 37 celdas, 18 de código ejecutadas y cero errores guardados. Las comprobaciones de invariancia, particiones, capital, benchmark y frontend local se reejecutaron y pasaron. La responsabilidad de comprender/verificar personalmente el trabajo y describir honestamente la asistencia IA corresponde al alumno.

El modelo de retorno oficial es XGBoost pooled con doce features; el modelo de riesgo oficial es XGBoost individual con las mismas doce features. La selección procede de validación anterior a 2024. El proyecto estudia inversión a cinco sesiones, no day trading ni resultados reales de 2026. Los experimentos están en la carpeta hermana experimentos y no forman parte del modelo entregado.

El frontend histórico original ya existe y fue probado localmente. Se está preparando una entrada de despliegue con el modelo oficial. Repositorio independiente de entrega: https://github.com/lariza-amoros/stock-market-ml . La publicación completa del código y la URL de una aplicación activa deben verificarse por separado; crear un repositorio no confirma el despliegue. Caldero Verde es otro proyecto: solo se autorizó retirar stock_market.ipynb, conservando el resto.

## 2. Documentos que gobiernan la revisión
- Enunciado literal: [04_recursos/ASIGNACION_ORIGINAL.txt](../../04_recursos/ASIGNACION_ORIGINAL.txt).
- Auditoría vigente: [04_recursos/v2_results/REVISION_RUBRICA_2026-10-13.md](../../04_recursos/v2_results/REVISION_RUBRICA_2026-10-13.md).
- Estado actualizado al mínimo 70%: [04_recursos/v2_results/ESTADO_ACTUAL_70.md](../../04_recursos/v2_results/ESTADO_ACTUAL_70.md).
- README vigente: [README.md](../../README.md).
- Notebook principal: [01_notebooks/stock_market_proyecto_organizado.ipynb](../../01_notebooks/stock_market_proyecto_organizado.ipynb).

No usar README/notebooks de versiones anteriores como definición del pipeline actual. Se conserva el historial; los informes de auditoría antiguos están identificados como tales.

## 3. Datos y alcance temporal
Fuente de precios: snapshot de yfinance/Yahoo Finance, OHLCV ajustado. Cobertura: 2015-01-02 a 2025-12-31; 2,766 sesiones y 50 columnas; 0 nulos. Retornos diarios: 2,765 observaciones. Los cierres ajustados pueden revisarse por dividendos/splits y no constituyen una base plenamente point-in-time.

Acciones: AAPL, MSFT, NVDA, AMZN, GOOGL, JPM, XOM, JNJ. Sectores: tecnología, consumo discrecional, comunicaciones, finanzas, energía y salud. SPY y VIX se descargan adicionalmente. **SPY/S&P 500 solamente EDA y benchmark**: no son features, filas de entrenamiento, targets ni criterios de selección. VIX se usa únicamente en variantes de contexto B/C.

Archivo principal: [02_datos/v2/precios_yfinance.csv.gz](../../02_datos/v2/precios_yfinance.csv.gz). La ausencia de sesiones de fines de semana/festivos es normal. El inicio efectivo de features es 2015-02-02 por las ventanas históricas; la última señal etiquetada es 2025-12-22 porque se necesitan precios posteriores dentro de 2025. No se omite 2025 por volatilidad: **2024 y 2025 se evalúan juntos**.

## 4. EDA y controles de calidad
El proyecto contiene precios históricos, distribuciones de retornos, volatilidad anualizada, correlaciones y estadísticas descriptivas. Revisar [04_recursos/v2_results/descriptive_statistics.csv](../../04_recursos/v2_results/descriptive_statistics.csv), [04_recursos/v2_results/correlations.csv](../../04_recursos/v2_results/correlations.csv) y las figuras de 03_graficos/v2. El EDA Summary se encuentra en [04_recursos/v2_results/EDA_Summary.txt](../../04_recursos/v2_results/EDA_Summary.txt).

La correlación de todo el período es exploratoria, no se entrega al modelo. Riesgo elevado y retornos altos de una acción no aseguran comportamiento futuro. El universo fijo de ocho empresas supervivientes introduce selección/supervivencia.

## 5. Las doce características por acción
Los modelos reciben una tabla longitudinal: doce columnas técnicas, repetidas para ocho tickers; 96 combinaciones acción-variable, no necesariamente 96 columnas simultáneas.

| Variable | Cálculo | Información disponible |
|---|---|---|
| return_1 | Close(t)/Close(t−1)−1 | Cierre actual y anterior |
| return_5 | Close(t)/Close(t−5)−1 | Cinco sesiones pasadas |
| return_10 | Close(t)/Close(t−10)−1 | Diez sesiones pasadas |
| return_20 | Close(t)/Close(t−20)−1 | Veinte sesiones pasadas |
| ma5_ratio | Close/SMA5−1 | Media histórica cinco sesiones |
| ma20_ratio | Close/SMA20−1 | Media histórica veinte sesiones |
| volatility_5 | Std de retornos diarios, ventana 5 | Solo retornos conocidos |
| volatility_20 | Std de retornos diarios, ventana 20 | Solo retornos conocidos |
| volume_change | Volume(t)/Volume(t−1)−1 | Volumen conocido al cierre |
| volume_ratio20 | Volume/SMA20(Volume) | Volumen relativo |
| rsi14 | RSI con medias exponenciales alpha=1/14 | Ganancias/pérdidas pasadas |
| macd_ratio | (EMA12−EMA26)/Close | Tendencia normalizada |

Revisar [05_codigo/v2/features.py:53](../../05_codigo/v2/features.py#L53). NaN/infinito se excluyen al preparar filas elegibles. Los modelos de árbol no requieren estandarizar estas features. El pooled añade one-hot del ticker; no cuenta como nueva feature financiera.

Grupos originales: **A** doce técnicas; **B** A + VIX, tasa Fed, cambio acumulado de tasa en veinte sesiones y días desde política; **C** B + conteos de aranceles, salud y guerra en veinte sesiones. Los seis eventos se documentan con fuentes en events.csv. Su selección retrospectiva es una limitación; no constituye un feed completo de noticias ni prueba causal. Contexto disponible desde la sesión posterior a la fecha fuente. La tasa previa a 2015 sirve como estado inicial, no como resultado bursátil fuera del período.

## 6. Targets y unidades
**Retorno académico:** R(t,t+5)=Close(t+5)/Close(t)−1. Es regresión a cinco cierres. **Riesgo:** desviación estándar de los cinco retornos futuros, multiplicada por sqrt(252). Clase alta si supera el percentil 75 por ticker estimado con entrenamiento. Decision threshold original para probabilidades: 0.5.

**Retorno ejecutable:** Open(t+6)/Open(t+1)−1. Señal al cierre t, compra en apertura siguiente y liquidación cinco sesiones después. No es idéntico al target cierre-a-cierre; deben revisarse separadamente.

Umbrales de riesgo del entrenamiento final (volatilidad anualizada, no probabilidad):

| ticker | Umbral anualizado (%) |
|---|---|
| AAPL | 30.881 |
| AMZN | 34.673 |
| GOOGL | 29.887 |
| JNJ | 18.2 |
| JPM | 26.669 |
| MSFT | 29.428 |
| NVDA | 50.655 |
| XOM | 30.109 |

Los umbrales se recalculan por partición; no se estiman usando el test. Las etiquetas finales son iguales entre pooled/individual y algoritmos. Cualquier comparación futura debe mantener esta igualdad.

## 7. Particiones y prevención de fuga
21,920 filas etiquetadas en total. Desarrollo: 15,912 filas de entrenamiento anteriores a 2023 y 1,960 de validación 2023. Entrenamiento final: 17,912 filas anteriores a 2024; test: 3,968 filas de señales 2024-01-02 a 2025-12-22. La suma no coincide necesariamente con toda la tabla por la purga de etiquetas de frontera.

Revisar [05_codigo/v2/features.py:89](../../05_codigo/v2/features.py#L89). Se exige target_end anterior al inicio de la partición siguiente. Las fechas son cronológicas; no hay train_test_split aleatorio. El entrenamiento inicial es 2015–2022; validación 2023; ajuste final 2015–2023; prueba 2024–2025. El proyecto incluye walk-forward 2021/2022 con ajuste en años anteriores.

Los resultados 2024–2025 ya fueron observados. El modelo original fue seleccionado antes de su evaluación, pero posteriores experimentos son exploratorios; no se puede recuperar un test intacto reejecutándolo. No incorporar noticias posteriores ni revisiones futuras para mejorar retrospectivamente.

## 8. Algoritmos y búsqueda
RandomForestRegressor, RandomForestClassifier, XGBRegressor y XGBClassifier. Semilla 42, 80 árboles en la versión original, n_jobs=2. RF ajusta max_depth=[3,6] y min_samples_leaf=[10,30]. XGB ajusta max_depth=[2,4] y learning_rate=[0.03,0.1]; subsample=.8 y colsample_bytree=.8. Cuatro combinaciones por búsqueda; tres grupos × dos arquitecturas × dos algoritmos × dos tareas × cuatro configuraciones = 96 evaluaciones de desarrollo.

Pooled: un modelo para todas las acciones y ticker one-hot. Individual: ocho modelos separados. La evaluación final contiene 24 conjuntos de modelos; el hecho de que un conjunto individual contenga ocho pipelines no significa 24 pipelines únicamente. Selección de retornos por MAE de validación; selección de riesgo por F1, no por accuracy máxima del test.

Configuración oficial: retorno A/pooled/XGB, max_depth=2, learning_rate=.03; riesgo A/individual/XGB, max_depth=4, learning_rate=.1; ambos 80 árboles. Parámetros y elección: [04_recursos/v2_results/frozen_choices.json](../../04_recursos/v2_results/frozen_choices.json). Modelo serializado: [04_recursos/v2_results/models.joblib](../../04_recursos/v2_results/models.joblib). Revisar factory/fit_predict/develop/evaluate en models.py; no cargar modelos joblib de fuentes desconocidas.

## 9. Métricas de regresión completas
MAE/RMSE se expresan abajo en **puntos porcentuales de retorno**; dirección en %. Spearman evalúa asociación de rangos, no porcentaje de aciertos.

| group | architecture | algorithm | MAE (pp) | RMSE (pp) | Direccion (%) | Spearman |
|---|---|---|---|---|---|---|
| A | pooled | RF | 2.9732 | 4.0779 | 58.0897 | 0.0707 |
| A | pooled | XGB | 2.9626 | 4.059 | 58.1653 | 0.0753 |
| A | individual | RF | 2.9839 | 4.0955 | 56.376 | 0.0428 |
| A | individual | XGB | 2.9806 | 4.0755 | 56.754 | 0.0445 |
| B | pooled | RF | 3.3202 | 4.6193 | 57.9385 | 0.0759 |
| B | pooled | XGB | 3.081 | 4.1756 | 58.1653 | 0.0641 |
| B | individual | RF | 2.9893 | 4.0991 | 55.0151 | 0.0308 |
| B | individual | XGB | 2.9863 | 4.0884 | 56.9052 | 0.0399 |
| C | pooled | RF | 3.3202 | 4.6193 | 57.9385 | 0.0759 |
| C | pooled | XGB | 3.0832 | 4.1772 | 58.1401 | 0.0673 |
| C | individual | RF | 2.9893 | 4.0991 | 55.0151 | 0.0308 |
| C | individual | XGB | 2.982 | 4.0881 | 57.7117 | 0.047 |

Baseline obligatorio: cero retorno; MAE aproximado 3.0225 pp y RMSE 4.1176 pp. Oficial XGB A pooled: MAE 2.9626 pp, dirección 58.1653%, Spearman .0753. La mejora de error es pequeña; Spearman bajo limita la evidencia de ranking estable.

**Diagnóstico adicional calculado para este informe:** predecir siempre subida obtiene **58.54%** sobre las mismas filas de prueba. Esto supera ligeramente el acierto de dirección oficial 58.17%; no hay evidencia de ventaja direccional frente a esa regla trivial. No reemplaza el baseline cero exigido ni modifica las métricas originales. Un backtest rentable no demuestra que la dirección se prediga mejor.

### Justificación del hallazgo «siempre sube»
La unidad evaluada es una pareja **acción-fecha**, con retorno futuro a cinco cierres; no una operación independiente ni una predicción de todo el S&P 500. De 3,968 filas, **2,323** tienen retorno positivo y **1,645** retorno negativo o cero. Una regla que diga siempre «sube» acierta 2,323/3,968 = **58.5433%**, sin aprender ninguna variable. Esta proporción refleja la frecuencia de retornos positivos en estas ocho acciones durante la muestra, no una ley del mercado.

XGBoost acierta **2,308/3,968 = 58.1653%**. Predice subida en **3,875** casos (97.66%) y bajada en **93**. Entre esas 93 señales de bajada detecta correctamente **39** casos negativos/no positivos, pero se equivoca en **54** casos que realmente suben. Frente a «siempre sube», gana 39 aciertos y pierde 54: saldo **−15 aciertos**, diferencia **−0.3780 puntos porcentuales**.

Esto demuestra una inclinación alcista de las predicciones observadas. Es compatible con estimaciones de regresión cercanas a medias históricas positivas, pero no prueba que esa sea la única causa ni que el modelo carezca de todo valor. La selección de acciones supervivientes y el período concreto condicionan el resultado. No se debe redefinir la métrica como «porcentaje de precio acertado» para ocultar esta comparación.

Por año, sin excluir 2025:

| year | observations | always_up | model |
|---|---|---|---|
| 2024 | 2016 | 57.7381 | 56.8948 |
| 2025 | 1952 | 59.375 | 59.4775 |

El modelo queda por debajo de la regla en 2024 y ligeramente por encima en 2025. La diferencia global es pequeña y **descriptiva**: los targets se solapan cinco sesiones y las acciones están correlacionadas, por lo que 3,968 filas no son 3,968 pruebas independientes. Este informe no afirma que la superioridad del baseline sea estadísticamente concluyente. La comparación se añadió retrospectivamente y debe tratarse como diagnóstico exploratorio.

El baseline cero del enunciado sigue siendo obligatorio: su MAE mide magnitud del retorno, mientras «siempre sube» compara exclusivamente dirección. No hay un pronóstico de magnitud ni un ranking de acciones en esta regla. Por eso no determina el resultado de ML top 3: la cartera elige solamente tres acciones, usa fechas de rebalanceo no solapadas, pesos, costos y tamaños de ganancias/pérdidas. El 126.06% de retorno de cartera no contradice el 58.17% de acierto sobre las ocho acciones; son preguntas diferentes. Tampoco garantiza que el ranking sea estable o que el rendimiento se repita.

## 10. Métricas de riesgo completas
Accuracy/precision/recall/F1 se expresan en %. ROC-AUC en [0,1]. Precision: proporción de alarmas correctas. Recall: proporción de casos de alto riesgo detectados. F1 combina ambas, no equivale a accuracy.

| group | architecture | algorithm | Accuracy | Precision | Recall | F1 | ROC_AUC |
|---|---|---|---|---|---|---|---|
| A | pooled | RF | 79.8891 | 51.1538 | 16.5423 | 25.0 | 0.636 |
| A | pooled | XGB | 79.5111 | 48.6486 | 20.1493 | 28.496 | 0.6541 |
| A | individual | RF | 79.3599 | 47.6636 | 19.0299 | 27.2 | 0.6506 |
| A | individual | XGB | 77.9486 | 41.7633 | 22.3881 | 29.1498 | 0.633 |
| B | pooled | RF | 80.494 | 57.9787 | 13.5572 | 21.9758 | 0.6356 |
| B | pooled | XGB | 79.1835 | 45.6693 | 14.4279 | 21.9282 | 0.6108 |
| B | individual | RF | 80.0655 | 52.9412 | 14.5522 | 22.8293 | 0.6471 |
| B | individual | XGB | 78.3266 | 41.5663 | 17.1642 | 24.2958 | 0.6064 |
| C | pooled | RF | 80.5948 | 59.6591 | 13.0597 | 21.4286 | 0.6301 |
| C | pooled | XGB | 80.0151 | 52.6066 | 13.806 | 21.8719 | 0.635 |
| C | individual | RF | 80.0655 | 52.8889 | 14.801 | 23.1293 | 0.6523 |
| C | individual | XGB | 77.7722 | 38.0368 | 15.4229 | 21.9469 | 0.6143 |

Clasificador oficial A individual XGB: accuracy 77.95%, precision 41.76%, recall 22.39%, F1 29.15%, ROC-AUC .6330. **Accuracy máxima** entre todos los modelos: 80.59%, C pooled RF, con F1 21.43% y recall 13.06%. No cambiar la elección oficial porque otro modelo tenga mayor accuracy en el test.

Baseline mayoritario: **79.74%** de accuracy, F1/recall de alto riesgo cero. Superar 70% en accuracy puede resultar de predecir siempre riesgo normal. Las probabilidades originales no fueron calibradas; no tratarlas como certeza de pérdidas o de ganar dinero.

## 11. Mínimo adicional del 70%
El enunciado literal no impone una exactitud mínima ni exige superar el mercado. El usuario actualizó el objetivo adicional a 70%; todavía debe precisarse la métrica/fórmula.
- Accuracy de riesgo oficial 77.95% y máximo 80.59% superan 70%.
- Acierto de dirección máximo 58.17% no alcanza 70%.
- F1 oficial 29.15% no alcanza 70% si ese fuera el criterio.
- Rentabilidad de cartera 126.06% no equivale a exactitud.

No se certifica cumplimiento global del mínimo mezclando porcentajes distintos. La documentación vigente refleja 70%, sin alterar modelos, datos o resultados.

## 12. Estrategias originales y ejecución
1. Equal weight: ocho acciones con pesos iguales.
2. ML top 3: tres acciones de mayor retorno predicho; pesos iguales. La implementación original no exige retorno predicho positivo.
3. Risk aware ML: clasificar primero; elegir hasta tres de mayor retorno previsto entre acciones etiquetadas normales. Si ninguna es elegible, efectivo. **No hay stop-loss, trailing stop ni take-profit**. Las salidas mantienen el calendario de cinco sesiones.
4. SPY: buy-and-hold en fechas equivalentes, solo benchmark.

Revisar [05_codigo/v2/portfolios.py:6](../../05_codigo/v2/portfolios.py#L6). Costos: 10 bps por lado aplicados al turnover de pesos, más liquidación terminal; SPY sin comisión por convención original. Valoración diaria a cierre y salida/apertura final; capital inicial $100,000. Sharpe usa tasa libre de riesgo cero, sin interés para efectivo. No se modelan impuestos, ejecución intradía, impacto de mercado ni spreads observados.

## 13. Resultados de cartera
Retornos/volatilidad/drawdown en %. Período ejecutable: 2024-01-03 a 2025-12-31.

| strategy | total_return | annualized_return | annualized_volatility | Sharpe_rf_zero | max_drawdown | final_capital |
|---|---|---|---|---|---|---|
| Equal weight | 87.623 | 37.1236 | 17.6144 | 1.8855 | -19.5377 | 187623.0322 |
| ML top 3 | 126.0597 | 50.5635 | 23.9546 | 1.8335 | -26.5056 | 226059.6788 |
| Risk aware ML | 62.5275 | 27.5926 | 21.4796 | 1.2457 | -37.6479 | 162527.506 |
| SPY | 49.6773 | 22.4274 | 16.3576 | 1.3217 | -18.7552 | 149677.278 |

ML top tres supera SPY y equiponderada en rentabilidad histórica, pero su drawdown es mayor. Equiponderada tiene Sharpe ligeramente superior a ML top tres. Risk aware tiene menor rentabilidad y mayor drawdown que ML top tres: el filtro original no aportó protección suficiente. No atribuirlo a salidas tardías/tempranas, pues ese filtro solo cambia selección de acciones.

## 14. Beneficio/pérdida por período
Se reconstruyeron cien períodos de cartera de cinco sesiones usando aperturas, holdings y costos; el capital final coincide con portfolio_metrics.csv. No son operaciones individuales por acción.

| Estrategia | Períodos ganadores | Ganancia media | Pérdida media | Ganancia/pérdida media |
|---|---:|---:|---:|---:|
| ML top 3 | 66/100 | +2.8608% | −2.9527% | .9689 |
| Risk aware ML | 68/100 | +2.2931% | −3.1794% | .7212 |
| Equal weight | 67/100 | +1.9276% | −1.8838% | 1.0232 |

La frecuencia de ganancia de la cartera no es el acierto de dirección de las ocho acciones. Capital compuesto y exposición afectan los promedios en dólares. No usar −2.95% como stop óptimo ni asumir que puede garantizarse esa pérdida máxima.

## 15. Importancia y discusión científica
Las figuras muestran diez variables financieras para RF/XGB y ambas tareas; excluyen ticker one-hot del ranking financiero. Los scores son impurity/gain, no relaciones causales ni importancia universal. Variables correlacionadas pueden repartir/distorsionar importancia. Revisar [04_recursos/v2_results/feature_importance.csv](../../04_recursos/v2_results/feature_importance.csv) y figuras correspondientes.

Las siete preguntas obligatorias se responden en Markdown del notebook: comparación de algoritmos; dificultad retorno/riesgo; pooled vs individuales; superar SPY; métricas vs retornos; evidencia de generalización; limitaciones/mejoras. Las comparaciones A/B/C no muestran mejora causal robusta de los seis eventos. Los intervalos por bloques del proyecto original son aproximados.

## 16. Rúbrica y evidencia de debug
| Componente | Peso | Estado | Evidencia |
|---|---|---|---|
| Datos/EDA | 15% | Implementado | Precios, retornos, nulos, volatilidad y correlaciones |
| Features/leakage | 15% | Implementado | 12 × 8, targets, purga e invariancia |
| RF/XGBoost | 20% | Implementado | Regresión/clasificación, pooled/individual, ajuste |
| Evaluación | 20% | Implementado | Todas las métricas y baselines |
| Carteras | 15% | Implementado | Tres estrategias + SPY, costos, capital y riesgo |
| Interpretación/notebook | 15% | Implementado técnicamente | Diez features, siete preguntas y declaración IA |

Pruebas implementadas y ejecutadas en work/verify_v2.py: 12×8, SPY alterado no cambia features/targets, cambios futuros no alteran features anteriores, límites purgados, fórmula cierre t+5, cuatro carteras comienzan con $100,000, fechas anteriores a 2026, SPY reproduce buy-and-hold, etiquetas pooled/individual consistentes, frontend produce ocho pronósticos y demo registra una operación.

Pruebas Streamlit AppTest verifican funcionalidad, no certifican todo diseño visual o publicación externa. El notebook completo se ejecutó previamente; en la última revisión documental se comprobó su estructura, sus 18 execution_count y ausencia de outputs de error. No confundir esa inspección con un reentrenamiento nuevo. Se corrigieron SPY en inputs, separación target/ejecución, purga temporal y etiquetas de figuras. Ver [04_recursos/v2_results/VERIFICACION_REAL.txt](../../04_recursos/v2_results/VERIFICACION_REAL.txt).

## 17. Frontend: estado real y cierre de entrega
El original app.py ya ofrece Predicciones, Resultados y Cuenta demo; datos históricos 2024–2025, ocho acciones, selección A/B/C/algoritmo/arquitectura, comparación posterior opcional, capital demo y CSV. La cuenta es local e histórica, sin bróker. El usuario puede reiniciarla; no hay persistencia externa.

Antes de entregar la entrada de despliegue: usar por defecto las elecciones oficiales congeladas, separar claramente predicción y resultado real, mostrar unidades y fechas, verificar capital/costos/orden cronológico, enlazar notebook/informe, probar instalación y documentar Python. El frontend original permite elegir un mismo algoritmo/arquitectura para ambas tareas; ese par no siempre coincide con el par oficial pooled-retorno/individual-riesgo. La entrada de entrega debe hacerlo explícito.

Despliegue recomendado: Streamlit Community Cloud, repositorio stock-market-ml, branch main, archivo streamlit_app.py, Python 3.12. Un enlace al formulario de despliegue no es una URL de app funcionando. No publicar secretos, credenciales, venv, caches ni experimentos como modelo oficial. Dependencias/modelos/datos deben estar incluidos o reproducibles.

## 18. GitHub y estructura de entrega
Repo objetivo independiente: lariza-amoros/stock-market-ml. Eliminar únicamente stock_market.ipynb del repositorio Caldero Verde mediante commit recuperable, tras guardar la copia y verificar su Git blob SHA. No borrar Caldero Verde ni su historial. El permiso del conector de GitHub rechazó inicialmente la escritura (HTTP 403); la sesión de navegador está autenticada y se usa como alternativa autorizada.

La entrega debe contener notebook vigente, módulos v2, snapshot de datos, modelos entrenados, métricas, figuras, informe, README, requirements, frontend y .gitignore. Experimentos y versiones históricas no se consideran modelo oficial; no subir archivos duplicados/ZIPs gigantes innecesarios. Comprobar clone limpio, referencias de rutas, tamaño de archivos y arranque de frontend antes de afirmar publicación completa.

## 19. Ruta de revisión del código
| Orden | Archivo/función | Qué verificar |
|---|---|---|
| 1 | [05_codigo/v2/features.py:14](../../05_codigo/v2/features.py#L14) | Fecha mínima/máxima, columnas y nulos |
| 2 | [05_codigo/v2/features.py:26](../../05_codigo/v2/features.py#L26) | Disponibilidad de tasas/eventos |
| 3 | [05_codigo/v2/features.py:53](../../05_codigo/v2/features.py#L53) | Doce fórmulas, targets, NaN y sin futuro |
| 4 | [05_codigo/v2/features.py:89](../../05_codigo/v2/features.py#L89) | Purga por target_end y fechas |
| 5 | [05_codigo/v2/models.py:19](../../05_codigo/v2/models.py#L19) | Algoritmos, semillas, one-hot e hiperparámetros |
| 6 | [05_codigo/v2/models.py:39](../../05_codigo/v2/models.py#L39) | Etiquetas, umbral por ticker, baselines y probabilidades |
| 7 | [05_codigo/v2/models.py:67](../../05_codigo/v2/models.py#L67) | Selección solo con validación y walk-forward |
| 8 | [05_codigo/v2/models.py:108](../../05_codigo/v2/models.py#L108) | Misma prueba, métricas y variantes |
| 9 | [05_codigo/v2/portfolios.py:6](../../05_codigo/v2/portfolios.py#L6) | Señal/ejecución, costos, posiciones, valoración y capital |
| 10 | [05_codigo/v2/research.py:110](../../05_codigo/v2/research.py#L110) | Coordinación del pipeline y archivos |
| 11 | [05_codigo/v2/app.py:30](../../05_codigo/v2/app.py#L30) | Inferencia con modelos guardados, demo y presentación |

## 20. Mapa del notebook para revisión celda a celda
| Celda | Tipo | Inicio | Ejecutada |
|---|---|---|---|
| 1 | markdown | # Can Machine Learning Beat the Stock Market? | — |
| 2 | markdown | ## 1. Data Collection and Exploratory Analysis | — |
| 3 | markdown | ### 1.1 Environment, data acquisition and snapshot | — |
| 4 | code | import importlib.util, subprocess, sys | 1 |
| 5 | code | import base64, os, sys | 2 |
| 6 | code | REFRESH_DATA=False | 3 |
| 7 | markdown | ### 1.2 Reproducible support modules | — |
| 8 | code | %%writefile _stock_market_code/features.py | 4 |
| 9 | code | %%writefile _stock_market_code/models.py | 5 |
| 10 | code | %%writefile _stock_market_code/portfolios.py | 6 |
| 11 | code | %%writefile _stock_market_code/research.py | 7 |
| 12 | markdown | ### 1.3 Data quality and exploratory statistics | — |
| 13 | code | from features import load_inputs,engineer,TECH,STOCKS,GROUPS,split | 8 |
| 14 | markdown | ### 1.4 Required EDA visualizations | — |
| 15 | code | import matplotlib.pyplot as plt | 9 |
| 16 | markdown | ## 2. Feature Engineering | — |
| 17 | code | data,ready=engineer(raw,policy,events) | 10 |
| 18 | markdown | ## 3. Prediction Targets | — |
| 19 | code | display(data[['date','ticker','target_return','target_volatility','target_end','execution_return']].head(16)) | 11 |
| 20 | markdown | ## 4. Machine Learning Model Development | — |
| 21 | markdown | ### 4.1 Training, tuning, chronological evaluation and baselines | — |
| 22 | code | from research import run | 12 |
| 23 | markdown | ## 5. Portfolio Simulation | — |
| 24 | code | display(result['performance']) | 13 |
| 25 | markdown | ## 6. Model Interpretation and Scientific Discussion | — |
| 26 | code | for image in sorted((PROJECT/'03_graficos/v2').glob('feature_importance_*.png')): | 14 |
| 27 | markdown | ### 6.2 Interpretation of financial predictors | — |
| 28 | markdown | ### 6.3 Critical thinking: seven required answers | — |
| 29 | markdown | ### 6.4 Detailed reproducible discussion | — |
| 30 | code | display(Markdown(result["report"])) | 15 |
| 31 | markdown | ## Final Deliverable | — |
| 32 | code | import hashlib,json | 16 |
| 33 | markdown | ### Optional historical inference demo | — |
| 34 | code | SIGNAL_DATE=raw.index[-7] | 17 |
| 35 | markdown | ### Final validation checks | — |
| 36 | code | # Independent executable checks of AI-assisted implementation | 18 |
| 37 | markdown | ### AI assistance — disclosure and verified corrections | — |

## 21. Pendientes y límites de cierre
| Ítem | Estado | Criterio de cierre |
|---|---|---|
| Pipeline académico y rúbrica | Implementado/verificado | Mantener ejecución reproducible y explicaciones |
| Objetivo adicional 70% | Métrica pendiente de precisar | No declarar dirección/F1 >=70% |
| Revisión personal y uso de IA | Responsabilidad del alumno | Reproducir y explicar una corrección propia |
| Frontend local | Implementado/probado | Entrada oficial de entrega y prueba final de paquete |
| Repo independiente | Creado; carga/validación por verificar | Archivos completos y commit comprobado |
| Retirar notebook de Caldero Verde | Autorizado; respaldado; escritura por verificar | Commit que retire solo ese archivo |
| Deploy de frontend | Usuario solicitó enlace para hacerlo | Formulario preparado; URL activa tras deploy |
| Experimentos | Separados | No sustituir original sin nueva evidencia |

## 22. Archivos de evidencia que deben acompañar la revisión
model_metrics.csv, hyperparameter_tuning.csv, walk_forward.csv, frozen_choices.json, predictions_*.csv.gz, portfolio_metrics.csv, portfolio_equity.csv, trades.csv, feature_importance.csv, event_significance.csv, descriptive_statistics.csv y correlations.csv. Se guardan bajo 04_recursos/v2_results. Un lector debe poder reconstruir las cifras de este informe a partir de esos archivos.

## 23. Reproducibilidad y conservación
Python 3.12 y versiones documentadas en requirements.txt. El frontend lee modelos/datos guardados y no requiere entrenar en cada sesión. Ejecutar research.py recalcula resultados, por lo que conviene usar una copia/versionado para conservar snapshots originales. El notebook principal genera su propio código/datos de trabajo; no depende de scripts externos para el entregable académico. Modelos y datos originales no se alteraron para este informe.

El generador de este informe es work/build_project_report.py. Las tablas se derivan de archivos originales; el baseline siempre-subida se añadió como diagnóstico explícito, no como sustitución retrospectiva del modelo. Antes de calificar cualquier variante como mejor, revisar error, baselines, riesgo, costos y estabilidad temporal juntos.
