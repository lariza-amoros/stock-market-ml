# Can Machine Learning Beat the Stock Market?

## Project report and scientific discussion

**Updated: October 13, 2026.** This report documents the final implementation, development decisions, verified results, debugging, and remaining limitations. All numerical results are preserved; this update changes documentation only.

## 1. Objective and constraints

Evaluate whether Random Forest (RF) and XGBoost (XGB) can predict five-session stock returns and high-volatility risk, and whether those forecasts support portfolios that outperform SPY.

- Historical data: January 2015–December 2025. No 2026 market outcomes are used.
- Stocks: AAPL, MSFT, NVDA, AMZN, GOOGL, JPM, XOM, and JNJ.
- SPY/S&P 500: visualization and benchmark only; excluded from predictors, training rows, targets, and model selection. VIX is permitted in context experiments.
- Academic submission: one notebook containing acquisition, EDA, features, targets, models, evaluation, portfolios, interpretation, limitations, and AI disclosure.
- The rubric does not require beating the market or achieving a minimum accuracy. The separate user-defined target is 70%; its metric must be specified. It is not an additional 90–95% requirement.

## 2. Development strategy

The workflow was: historical snapshot and EDA → twelve technical features per stock → five-session targets → purged chronological development → hyperparameter tuning → RF/XGB and pooled/individual comparisons → context ablation → portfolio simulation → scientific interpretation and debugging.

Data quality checks covered dates, missing values, prices, distributions, volatility, and correlations. The price snapshot contains 2,766 trading sessions, 50 columns, and no missing values, from January 2, 2015 through December 31, 2025. Daily returns have 2,765 observations. Adjusted OHLCV data originate from yfinance/Yahoo Finance; revisions to split/dividend-adjusted history remain a limitation.

Each stock has twelve technical predictors: returns over 1/5/10/20 sessions; price-to-moving-average ratios over 5/20 sessions; rolling volatility over 5/20 sessions; daily volume change; volume-to-20-session-average ratio; RSI14; and normalized MACD. This is 12 × 8 stock-feature combinations in a longitudinal table, not 96 independent predictors in every stock row.

The context comparisons use three groups:

| Group | Inputs |
|---|---|
| A | Twelve technical features |
| B | Technical features plus VIX and monetary-policy context |
| C | Group B plus dated historical-event indicators |

Tariff announcements, COVID-19, and war-related events were represented with dated sources. Policy/event information becomes available from the following observed trading session. The catalogue is small and retrospective; it does not constitute causal evidence or a complete point-in-time macroeconomic database. Experiments remain separate from the original official model.

## 3. Targets and leakage prevention

The academic return target is **close(t+5) / close(t) − 1**. The risk target classifies high volatility over the following five daily returns using a per-stock 75th-percentile threshold estimated from training data. Execution returns are separate: portfolio entries occur at the next session's open, rather than at the signal close.

Development uses observations before 2024, validation in 2023, and a common final test covering both 2024 and 2025. Targets that cross a temporal boundary are excluded. Earlier walk-forward windows provide additional development checks. The final test has now been observed: new tuning against its results would be exploratory, not a fresh holdout evaluation.

Predictors start on February 2, 2015 because rolling windows require history. The last labelled signal is December 22, 2025; subsequent prices needed for targets/execution remain inside 2025. The project does not exclude 2025 because of instability.

## 4. Models and selection

RF and XGB were implemented for both regression and classification, with pooled and stock-specific models. Pooled models include ticker encoding. The shared hyperparameter grids are:

| Algorithm | Tuned parameters |
|---|---|
| RF | max_depth: 3 or 6; min_samples_leaf: 10 or 30 |
| XGB | max_depth: 2 or 4; learning_rate: 0.03 or 0.10 |

The evaluated models use 80 trees and random seed 42. Model selection was based on validation results and frozen before final testing, not on final portfolio returns.

The official return model is **group A, pooled XGBoost**. The official risk model is **group A, stock-specific XGBoost**. The maximum test risk accuracy, **80.59%**, belongs to **group C, pooled RF**. It is a different model from the official risk classifier, whose accuracy is **77.95%**.

## 5. Regression results

All rows use the same 2024–2025 test period. MAE and RMSE below are percentage points (pp), not accuracy percentages.

| Group | Architecture | Algorithm | MAE (pp) | RMSE (pp) | Direction (%) | Spearman |
|---|---|---|---:|---:|---:|---:|
| A | pooled | RF | 2.9732 | 4.0779 | 58.09 | 0.0707 |
| A | pooled | XGB | 2.9626 | 4.0590 | 58.17 | 0.0753 |
| A | individual | RF | 2.9839 | 4.0955 | 56.38 | 0.0428 |
| A | individual | XGB | 2.9806 | 4.0755 | 56.75 | 0.0445 |
| B | pooled | RF | 3.3202 | 4.6193 | 57.94 | 0.0759 |
| B | pooled | XGB | 3.0810 | 4.1756 | 58.17 | 0.0641 |
| B | individual | RF | 2.9893 | 4.0991 | 55.02 | 0.0308 |
| B | individual | XGB | 2.9863 | 4.0884 | 56.91 | 0.0399 |
| C | pooled | RF | 3.3202 | 4.6193 | 57.94 | 0.0759 |
| C | pooled | XGB | 3.0832 | 4.1772 | 58.14 | 0.0673 |
| C | individual | RF | 2.9893 | 4.0991 | 55.02 | 0.0308 |
| C | individual | XGB | 2.9820 | 4.0881 | 57.71 | 0.0470 |

The zero-return baseline has MAE **3.0225 pp**, RMSE **4.1176 pp**, and directional accuracy **41.46%** under the implementation's positive-versus-nonpositive convention. Its constant forecasts do not provide a meaningful Spearman ranking.

The official model achieves MAE **2.9626 pp**, RMSE **4.0590 pp**, direction **58.17%**, and Spearman **0.0753**. These are modest predictive results, not a certified 70% price/direction accuracy.

### Why the “always up” baseline matters

The test contains 3,968 stock-date rows: 2,323 positive future returns and 1,645 nonpositive returns. Always predicting positive yields **58.5433%** direction accuracy. The official model gets 2,308 rows correct (**58.1653%**) and predicts up on 3,875 rows (**97.66%**).

Its 93 down predictions correctly identify 39 nonpositive outcomes but miss 54 positive outcomes: a net loss of 15 correct predictions, or **0.3780 percentage points**, relative to always up. By year, always up/model direction is **57.74%/56.89% in 2024** and **59.38%/59.48% in 2025**.

These are descriptive, retrospective diagnostics. Overlapping targets and correlated stocks mean the rows are not independent trials; no statistically conclusive baseline-superiority claim is made. Direction accuracy is also different from ranking quality and portfolio returns.

## 6. Risk-classification results

| Group | Architecture | Algorithm | Accuracy (%) | Precision (%) | Recall (%) | F1 (%) | ROC-AUC |
|---|---|---|---:|---:|---:|---:|---:|---:|
| A | pooled | RF | 79.89 | 51.15 | 16.54 | 25.00 | 0.6360 |
| A | pooled | XGB | 79.51 | 48.65 | 20.15 | 28.50 | 0.6541 |
| A | individual | RF | 79.36 | 47.66 | 19.03 | 27.20 | 0.6506 |
| A | individual | XGB | 77.95 | 41.76 | 22.39 | 29.15 | 0.6330 |
| B | pooled | RF | 80.49 | 57.98 | 13.56 | 21.98 | 0.6356 |
| B | pooled | XGB | 79.18 | 45.67 | 14.43 | 21.93 | 0.6108 |
| B | individual | RF | 80.07 | 52.94 | 14.55 | 22.83 | 0.6471 |
| B | individual | XGB | 78.33 | 41.57 | 17.16 | 24.30 | 0.6064 |
| C | pooled | RF | 80.59 | 59.66 | 13.06 | 21.43 | 0.6301 |
| C | pooled | XGB | 80.02 | 52.61 | 13.81 | 21.87 | 0.6350 |
| C | individual | RF | 80.07 | 52.89 | 14.80 | 23.13 | 0.6523 |
| C | individual | XGB | 77.77 | 38.04 | 15.42 | 21.95 | 0.6143 |

The majority-class baseline achieves **79.74% accuracy**, zero high-risk precision/recall/F1 under the stated convention, and ROC-AUC **0.50**. The official classifier has accuracy **77.95%**, precision **41.76%**, recall **22.39%**, F1 **29.15%**, and ROC-AUC **0.6330**.

The model with maximum accuracy (RF pooled C) has **80.59% accuracy**, but only **21.43% F1** and **13.06% recall**. High accuracy alone therefore does not demonstrate effective detection of the high-volatility minority class. Accuracy, F1, directional accuracy, and investment returns must not be interchanged.

## 7. Portfolio simulation

All strategies begin with **$100,000**, use matching dates, rebalance every five trading sessions, and execute at the next open. Daily closes mark portfolio equity between executable trades. Transaction costs are **10 basis points per side on traded turnover**, including investment and liquidation. Cash earns zero; Sharpe uses a zero risk-free rate. SPY follows the original no-fee benchmark convention.

| Strategy | Selection and allocation |
|---|---|
| Equal weight | Equal allocation across eight stocks |
| ML Top 3 | Equal allocation to the three highest predicted returns |
| Risk-aware ML | Rank returns among stocks predicted below the high-risk threshold; fewer positions or cash if necessary |
| SPY buy-and-hold | Market benchmark |

| Strategy | Total return (%) | Annualized return (%) | Annualized volatility (%) | Sharpe | Maximum drawdown (%) | Final capital ($) |
|---|---:|---:|---:|---:|---:|---:|
| Equal weight | 87.62 | 37.12 | 17.61 | 1.89 | -19.54 | 187623.03 |
| ML top 3 | 126.06 | 50.56 | 23.95 | 1.83 | -26.51 | 226059.68 |
| Risk aware ML | 62.53 | 27.59 | 21.48 | 1.25 | -37.65 | 162527.51 |
| SPY | 49.68 | 22.43 | 16.36 | 1.32 | -18.76 | 149677.28 |

ML Top 3 outperformed SPY in this historical test, with a larger maximum drawdown. The original risk-aware portfolio reduced return and worsened drawdown relative to Top 3. This supports a critical conclusion about this implementation, not a promise about future performance. The required combined equity chart is [portfolio_100000.png](../../03_graficos/v2/portfolio_100000.png).

## 8. Scientific discussion: seven required answers

### 1. Which algorithm performed better, and why?

For group A pooled returns, XGB achieved MAE 0.029626 versus RF 0.029732, and direction 58.17% versus 58.09%. The difference is small. Sequential boosting can model nonlinear relationships, but the experiment does not establish that architecture caused the improvement or that XGB avoids memorizing noise. For risk, RF pooled C achieved maximum accuracy; official selection was made using validation, not the maximum test score.

### 2. Was predicting returns more difficult than predicting volatility?

Return direction shows limited value beyond the always-up baseline. Volatility persistence is a plausible explanation for some risk predictability, not a causal finding established here. The tasks' percentages cannot be compared directly: official risk accuracy is below the majority baseline, and F1 is only 29.15%. High accuracy does not by itself establish useful high-risk detection.

### 3. Did pooled models outperform individual models?

Pooled models achieved lower return MAE in the reported comparisons. Sharing stock observations can support learning common patterns, but correlated rows are not eight times as much independent information. Risk results vary by algorithm, feature group, and metric; selecting an individual official risk model does not prove universal superiority.

### 4. Did the ML strategy outperform SPY?

Yes, within 2024–2025: Top 3 returned 126.06% versus SPY 49.68%, with drawdown −26.51% versus −18.76%. Ranking is the selection mechanism, but its causal contribution was not isolated. The experiment does not prove consistent superiority across other periods or live trading.

### 5. Did better predictive performance necessarily produce better investment returns?

No. Direction, prediction error, ranking, exposure, concentration, and transaction costs affect portfolios differently. Top 3 earned more despite not beating the directional baseline; the risk-aware strategy earned less and experienced deeper drawdown. The original risk filter did not demonstrate a better return/risk balance.

### 6. What evidence supports generalization?

Earlier-only validation/tuning, purged chronological partitions, training-only risk thresholds, matching test periods, and earlier walk-forward windows support out-of-training evaluation. They do not prove reliable future performance. Seeds, hashes, and successful reruns establish reproducibility and input integrity, not generalization. Future optimization against the observed test must be labelled exploratory.

### 7. What are the limitations, and how could the approach improve?

Limitations include a small universe of surviving stocks, revised adjusted prices, overlapping targets, correlated stocks, a retrospective event catalogue, weak high-risk recall, simplified costs, and a single two-year final test. Improvements to test separately include point-in-time releases, additional purged temporal validation, calibration/threshold selection using validation only, realistic liquidity/slippage assumptions, and prospective paper trading. No improvement guarantees 70%, 90%, or 95%; none should be tuned against the observed final test.

## 9. Interpretation and significance

The project provides top-ten feature-importance visualizations for RF and XGB, stock-level comparisons, and context/event ablation. Importance measures are internal impurity/gain scores, not causal effects; correlated inputs can distort attribution.

Context comparisons use paired prediction errors, approximate five-session block resampling, confidence intervals, and multiple-comparison correction. The results do not justify claiming that every event feature improves forecasts. See [event_significance.csv](event_significance.csv), [feature_importance.csv](feature_importance.csv), [walk_forward.csv](walk_forward.csv), and [hyperparameter_tuning.csv](hyperparameter_tuning.csv).

## 10. Code-review guide and rubric coverage

| Review area | File/evidence | Checks |
|---|---|---|
| Data and predictors | [features.py](../../05_codigo/v2/features.py) | Dates, twelve technical features, future targets, training-only thresholds, purged boundaries, no SPY inputs |
| Models and metrics | [models.py](../../05_codigo/v2/models.py) | RF/XGB, pooled/individual, grids, baselines, common evaluation periods |
| Trading | [portfolios.py](../../05_codigo/v2/portfolios.py) | Next-open execution, turnover costs, equal weights, risk selection, daily equity |
| Full experiment | [research.py](../../05_codigo/v2/research.py) | EDA, frozen choices, development, evaluation, saved outputs and discussion |
| Published frontend | [streamlit_app.py](../../streamlit_app.py) | Official model choices, dates/units, optional realized outcomes, demo chronology and costs |
| Notebook | [stock_market_proyecto_organizado.ipynb](../../01_notebooks/stock_market_proyecto_organizado.ipynb) | Complete ordered execution, six project sections, seven answers, AI disclosure |

| Rubric component | Weight | Implementation status |
|---|---:|---|
| Data collection and EDA | 15% | Present: quality checks, prices, return distributions, volatility and correlation |
| Feature engineering and leakage prevention | 15% | Present: twelve technical features per stock, targets and temporal controls |
| RF and XGB implementation | 20% | Present: regression/classification, pooled/individual and tuning |
| Evaluation and comparison | 20% | Present: all required metrics, baselines and comparable test dates |
| Portfolio simulation | 15% | Present: three stock strategies plus SPY, costs, all metrics and combined equity chart |
| Interpretation, conclusions and notebook quality | 15% | Present: importance, seven answers, limitations, reproducible notebook and AI disclosure |

This is an implementation audit, not a guaranteed grade. A scientifically valid negative result is acceptable under the assignment. The student must independently understand and explain the work.

## 11. Debugging and final verification

The current notebook has **38 cells, including 18 executed code cells**, and completed end-to-end without errors. Verification covered twelve features per stock, absence of SPY training inputs, invariance to future changes, chronological boundaries, target formulas, initial capital, benchmark reproduction, demo forecasts and chronology.

The Base64 data block was replaced by retrieval of the identical historical snapshot from a fixed GitHub commit. A remaining hash cell still attempted Base64 decoding and raised a NameError; it was corrected to hash the actual files with SHA-256. Verified input hashes and recomputed metrics match the originals. Normal notebook image outputs remain embedded; the code contains no Base64 data payload. Internet is required for initial snapshot retrieval.

The corrected notebook was backed up and updated in Drive, then published to GitHub under the existing notebook filename/link. The published Git blob was checked against the corrected Drive copy. No algorithms, hyperparameters, or numerical results were changed to reach an accuracy target.

## 12. Organization and delivery

The active folders are 01_notebooks, 02_datos/v2, 03_graficos/v2, 04_recursos/v2_results, and 05_codigo/v2. Current root documents are AGENTS.md, ENTREGA.md, and README.md. Earlier notebooks, previews, scripts, figures, documents, and archives were preserved in historical folders rather than deleted. Experiments remain separate from the official original model.

The current Drive notebook is [stock_market_proyecto.ipynb](https://colab.research.google.com/drive/1z8U_svyd6azRO73TQXV_cmT_qWsxkq8y). Drive's resultados_v2.zip contains models, 24 prediction files, equity, frozen choices, and trades; extract it into the expected results directory before running its app.py package.

The independent repository is [lariza-amoros/stock-market-ml](https://github.com/lariza-amoros/stock-market-ml). Caldero Verde remains separate; only its Stock Market notebook was removed through [recoverable commit 38db7bd](https://github.com/lariza-amoros/caldero-verde/commit/38db7bd9207ce25afaf7cf5a6cad83924900496f).

The [public Streamlit frontend](https://lariza-stock-market-ml.streamlit.app/) uses a black background and neon accents, official saved models, historical predictions and a virtual $100,000 account. Eight forecasts, a net-cost demo trade, overlapping-capital protection and reset were tested. The demo has no broker connection or real money; individual round-trip demo trades do not reproduce the turnover of the full continuous portfolio backtest. Uncalibrated risk scores indicate high-volatility classification, not probability of losing money.

Runtime: Python 3.12 with the documented [requirements](../../requirements.txt). The public app uses saved data/models and does not retrain on each interaction. The notebook generates its own code modules and outputs. Running the experiment writes results, so use a separate working copy to preserve original snapshots.

## 13. Remaining work and AI disclosure

No required evaluation metric is missing. Direction 58.17% and official risk F1 29.15% do not meet a separate 70% target; maximum risk accuracy 80.59% exceeds it, but does not establish overall compliance with an unspecified metric. The Drive research.py copy still contains old 90–95% wording; its computation matches, and its text should be synchronized separately. Personal student review and final submission remain necessary.

AI assisted with organization, draft code, debugging, feature engineering, visualization and writing. Verified corrections include removing SPY from training features, separating academic and executable returns, purging overlapping targets, checking historical feature invariance, and repairing snapshot/hash handling. The student should describe their own independent verification honestly; automated checks do not replace understanding or establish real-world trading reliability.
