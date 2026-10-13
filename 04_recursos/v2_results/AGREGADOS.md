# Lista de cambios para completar la asignación

1. Datos reales de yfinance, 2015-01-02 a 2025-12-31: 2,766 observaciones, 50 columnas, cero nulos. Snapshot reproducible incluido.
2. EDA Summary reescrito y uniforme, con seis secciones, estadísticas recalculadas, metodología y límites. Respaldo del Google Doc previo conservado.
3. Exactamente doce características técnicas para cada una de ocho acciones; SPY retirado de todas las entradas de entrenamiento.
4. Targets académicos de retorno a cinco cierres y riesgo futuro, separados de los retornos de ejecución a apertura siguiente.
5. Riesgo definido mediante percentil 75 de entrenamiento por acción, con etiquetas consistentes entre pooled e individual.
6. Random Forest y XGBoost para regresión y clasificación; pooled e individuales; tres grupos de variables A/B/C.
7. Dos hiperparámetros por algoritmo y cuatro configuraciones por búsqueda; validación 2023; dos ventanas walk-forward con tuning anterior; particiones purgadas.
8. MAE, RMSE, directional accuracy y Spearman; accuracy, precision, recall, F1 y ROC-AUC; baselines de retorno cero y clase mayoritaria.
9. Contexto VIX/política monetaria y seis eventos fechados de aranceles, COVID y guerra; fuentes oficiales; pruebas pareadas aproximadas y corrección múltiple.
10. Carteras equiponderada, ML top tres y ML consciente del riesgo, más SPY; $100,000, costes de 10 bps por lado, rebalanceo cada cinco sesiones, ejecución siguiente apertura y valoración diaria.
11. Todas las métricas de cartera, figura conjunta de capital y visualizaciones requeridas del EDA.
12. Diez características más importantes para ambos algoritmos y tareas; comparación entre acciones; discusión de las siete preguntas científicas, limitaciones y asistencia IA.
13. Notebook autónomo con código y datos incrustados; ejecución de principio a fin y resultados reales guardados.
14. Frontend Streamlit para ocho pronósticos históricos fuera de muestra y cuenta demo local con historial de operaciones.

Validación: ausencia de SPY en entrenamiento, invariancia ante cambios futuros, fechas purgadas, fórmula de target, capital inicial, equivalencia de SPY con buy-and-hold, consistencia de etiquetas, cálculo de pronósticos y operación demo.

El mínimo adicional indicado por el usuario es 70%. La métrica/fórmula no está definida: accuracy de riesgo máximo 80.6% supera ese nivel; acierto de dirección máximo 58.2% no lo alcanza. No confundir accuracy, F1 y rentabilidad ni declarar cumplimiento global del mínimo.
