# Results and critical discussion



## Model comparison

On final test, lowest MAE / highest F1 for return: XGB, group A, pooled; MAE=0.0296. This is a descriptive test comparison, not a new model-selection decision.

Baseline MAE range: 0.0302–0.0302.

On final test, lowest MAE / highest F1 for risk: XGB, group A, individual; F1=0.2915. This is a descriptive test comparison, not a new model-selection decision.

Baseline F1 range: 0.0000–0.0000.



## Returns versus risk

Return regression and risk classification use different metrics and cannot be ranked by raw percentages. Compare MAE against zero-return MAE and F1/accuracy against majority-class performance. Risk persistence may aid classification while short-horizon return direction remains noisy.



## Individual versus pooled

A/RF: pooled MAE 0.0297, individual MAE 0.0298.

A/XGB: pooled MAE 0.0296, individual MAE 0.0298.

B/RF: pooled MAE 0.0332, individual MAE 0.0299.

B/XGB: pooled MAE 0.0308, individual MAE 0.0299.

C/RF: pooled MAE 0.0332, individual MAE 0.0299.

C/XGB: pooled MAE 0.0308, individual MAE 0.0298.



## Portfolio results

SPY buy-and-hold total return on matching executable dates: 49.68%.

Equal weight: total return 87.62%; annualized 37.12%; volatility 17.61%; Sharpe (cash/risk-free assumed zero) 1.89; maximum drawdown -19.54%; final capital $187,623.03.

ML top 3: total return 126.06%; annualized 50.56%; volatility 23.95%; Sharpe (cash/risk-free assumed zero) 1.83; maximum drawdown -26.51%; final capital $226,059.68.

Risk aware ML: total return 62.53%; annualized 27.59%; volatility 21.48%; Sharpe (cash/risk-free assumed zero) 1.25; maximum drawdown -37.65%; final capital $162,527.51.

SPY: total return 49.68%; annualized 22.43%; volatility 16.36%; Sharpe (cash/risk-free assumed zero) 1.32; maximum drawdown -18.76%; final capital $149,677.28.

Better predictive metrics do not necessarily yield better investment returns: ranking, exposure, errors in selected stocks, turnover and costs alter portfolio outcomes. Portfolio models were selected on 2023 validation, not final returns.



## Economic and event significance

pooled/RF A→B: paired MAE improvement -0.003470; block-bootstrap 95% CI [-0.007139, -0.000599]; approximate block sign-flip p=0.1154; positive significant improvement after 12-comparison Bonferroni: False.

pooled/RF B→C: paired MAE improvement -0.000000; block-bootstrap 95% CI [-0.000000, 0.000000]; approximate block sign-flip p=0.1479; positive significant improvement after 12-comparison Bonferroni: False.

pooled/RF A→C: paired MAE improvement -0.003470; block-bootstrap 95% CI [-0.007410, -0.000581]; approximate block sign-flip p=0.1134; positive significant improvement after 12-comparison Bonferroni: False.

pooled/XGB A→B: paired MAE improvement -0.001184; block-bootstrap 95% CI [-0.002561, -0.000161]; approximate block sign-flip p=0.0905; positive significant improvement after 12-comparison Bonferroni: False.

pooled/XGB B→C: paired MAE improvement -0.000021; block-bootstrap 95% CI [-0.000046, 0.000001]; approximate block sign-flip p=0.0785; positive significant improvement after 12-comparison Bonferroni: False.

pooled/XGB A→C: paired MAE improvement -0.001206; block-bootstrap 95% CI [-0.002656, -0.000164]; approximate block sign-flip p=0.0740; positive significant improvement after 12-comparison Bonferroni: False.

individual/RF A→B: paired MAE improvement -0.000054; block-bootstrap 95% CI [-0.000239, 0.000116]; approximate block sign-flip p=0.5347; positive significant improvement after 12-comparison Bonferroni: False.

individual/RF B→C: paired MAE improvement 0.000000; block-bootstrap 95% CI [-0.000000, 0.000000]; approximate block sign-flip p=0.4523; positive significant improvement after 12-comparison Bonferroni: False.

individual/RF A→C: paired MAE improvement -0.000054; block-bootstrap 95% CI [-0.000230, 0.000119]; approximate block sign-flip p=0.5522; positive significant improvement after 12-comparison Bonferroni: False.

individual/XGB A→B: paired MAE improvement -0.000057; block-bootstrap 95% CI [-0.000307, 0.000158]; approximate block sign-flip p=0.6492; positive significant improvement after 12-comparison Bonferroni: False.

individual/XGB B→C: paired MAE improvement 0.000043; block-bootstrap 95% CI [-0.000028, 0.000134]; approximate block sign-flip p=0.3483; positive significant improvement after 12-comparison Bonferroni: False.

individual/XGB A→C: paired MAE improvement -0.000014; block-bootstrap 95% CI [-0.000212, 0.000184]; approximate block sign-flip p=0.8976; positive significant improvement after 12-comparison Bonferroni: False.

The uncertainty analysis aggregates across stocks by date and resamples approximately five-session blocks. It is an approximate test; financial dependence may extend beyond five sessions. A predictive association does not establish a causal impact of tariffs or wars. More features can worsen generalization.



## Interpretation

RF most important predictors: remainder__volatility_20, ticker__ticker_NVDA, remainder__volatility_5, remainder__ma5_ratio, remainder__return_20.

AAPL/RF: volatility_5, volatility_20, macd_ratio.

MSFT/RF: volatility_20, macd_ratio, return_5.

NVDA/RF: volatility_20, return_20, macd_ratio.

AMZN/RF: macd_ratio, volatility_5, volatility_20.

GOOGL/RF: macd_ratio, volatility_5, return_1.

JPM/RF: return_20, macd_ratio, ma20_ratio.

XOM/RF: volatility_20, macd_ratio, return_10.

JNJ/RF: volatility_20, volatility_5, ma20_ratio.

XGB most important predictors: remainder__ma5_ratio, remainder__volatility_20, remainder__return_20, remainder__return_10, remainder__volume_ratio20.

AAPL/XGB: volatility_5, rsi14, volatility_20.

MSFT/XGB: volatility_5, volatility_20, return_5.

NVDA/XGB: return_20, volatility_20, ma20_ratio.

AMZN/XGB: macd_ratio, volatility_5, return_20.

GOOGL/XGB: ma20_ratio, return_1, return_5.

JPM/XGB: volatility_5, volume_ratio20, ma20_ratio.

XOM/XGB: rsi14, macd_ratio, volume_ratio20.

JNJ/XGB: volatility_20, volatility_5, ma20_ratio.

Importance measures are model-internal impurity/gain scores, not causal effects; correlated predictors share or distort their attribution. Ticker one-hot columns in pooled models identify entities and are not additional financial features.



## Generalization evidence and limitations

Evidence: purged chronological partitions, earlier walk-forward windows with earlier-only tuning, training-only risk thresholds, identical test dates across algorithms, and zero-return/majority/equal-weight baselines. No SPY or S&P 500 data are supplied to model fitting.

Limitations: eight selected surviving stocks; revised dividend/split-adjusted history; small and retrospectively chosen event catalogue; target dates and transaction outcomes differ; no complete point-in-time CPI/employment dataset; zero interest on cash; no borrow, tax or market-impact model; only one two-year final test. Policy rates represent economic context but do not replace inflation or employment indicators. Non-significant improvements must not be presented as proof that events help.

The test period has now been inspected: future iterations must identify themselves as exploratory and use a fresh holdout or prospective paper trading for confirmatory validation. No 2026 results are used.

El mínimo adicional indicado por el usuario es 70%. La métrica/fórmula no está definida: accuracy de riesgo máximo 80.6% supera ese nivel; acierto de dirección máximo 58.2% no lo alcanza. No confundir accuracy, F1 y rentabilidad ni declarar cumplimiento global del mínimo.



## AI assistance

AI assisted with organization, code, feature engineering and writing. Verified corrections: removed SPY returns from training features; corrected the academic target to close(t+5)/close(t)-1; separated executable next-open portfolio returns; verified feature invariance to future-price changes and purged temporal boundaries. The student should review the code, independently reproduce these checks, interpret the outputs and describe their own verification before submission.
