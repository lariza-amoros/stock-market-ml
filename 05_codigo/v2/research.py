import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from features import PROJECT,STOCKS,TECH,GROUPS,load_inputs,engineer
from models import develop,evaluate,ablation
from portfolios import simulate


def eda_report(raw):
    closes=raw['Close']; returns=closes[STOCKS+['SPY']].pct_change(fill_method=None).dropna()
    stats=returns.describe().T
    stats.loc[:,stats.columns!='count']*=100
    corr=returns.corr()
    highest=stats['mean'].idxmax(); risk=stats['std'].idxmax(); lowest=stats['std'].idxmin()
    text=f'''Can Machine Learning Beat the Stock Market? — EDA Summary

1. Data scope and quality
The reproducible Yahoo Finance snapshot contains {len(raw):,} trading observations and {raw.shape[1]} columns, from {raw.index.min():%Y-%m-%d} to {raw.index.max():%Y-%m-%d}. It covers eight stocks across technology, consumer discretionary, communication services, financial services, energy and healthcare, plus SPY and VIX. There are {int(raw.isna().sum().sum())} missing values. Computing daily returns leaves {len(returns):,} observations because the first price has no preceding observation. No 2026 prices are used. Adjusted prices may differ from the earlier snapshot because the provider revises adjustments.

2. Return distribution and volatility
{highest} has the highest sample mean daily return ({stats.loc[highest,'mean']:.2f}%) and {risk} has the highest daily standard deviation ({stats.loc[risk,'std']:.2f}%). {lowest} has the lowest standard deviation ({stats.loc[lowest,'std']:.2f}%). SPY's mean daily return is {stats.loc['SPY','mean']:.2f}% and its daily standard deviation is {stats.loc['SPY','std']:.2f}%. These are descriptive averages, not guaranteed future returns. {risk}'s daily extremes are {stats.loc[risk,'min']:.2f}% and {stats.loc[risk,'max']:.2f}%. Extreme movements make both return and risk forecasting challenging.

3. Correlation and diversification
MSFT–SPY correlation is {corr.loc['MSFT','SPY']:.2f}, AAPL–SPY is {corr.loc['AAPL','SPY']:.2f}, and NVDA–JNJ is {corr.loc['NVDA','JNJ']:.2f}. Correlations describe historical co-movement and do not establish causation. Low correlation can support diversification, but relationships may change between market regimes. Full-period correlations are exploratory only and are not supplied to predictive models.

4. Figures and interpretation
The project includes labeled historical-price plots, daily-return distributions, annualized-volatility comparison and a correlation heatmap. Annualized historical volatility uses daily return standard deviation multiplied by sqrt(252). Market prices reflect noisy information, unexpected events, changing economic conditions and transaction costs; historical relationships may not generalize.

5. Modeling boundary
Each stock receives the same 12 technical features, calculated from information available at the signal date. SPY and S&P 500 are excluded from training rows, predictors and targets and are used only for exploratory comparison and portfolio benchmarking. VIX, Federal Reserve policy and documented events are assessed separately in feature ablations. Events are available from the next trading session after their dated announcement. Event selection is retrospective, so this experiment is exploratory rather than a causal estimate.

6. Evaluation protocol
Five-day closing-price return is the academic regression target. High-risk labels use each stock's training-only 75th percentile of future five-day annualized volatility. Chronological validation and target-boundary purging prevent overlap across partitions. Hyperparameter and model choices are frozen using data through 2023 before the 2024–2025 final test. Backtesting uses the next session's open, three investment strategies, an initial $100,000 and transaction costs. Predictive accuracy and investment return are separate outcomes; conclusions require the reported experiments and do not assume that the models outperform SPY.
'''
    return text,stats,corr


def figures(raw,equity,importance,folder):
    folder.mkdir(parents=True,exist_ok=True)
    close=raw['Close']; returns=close[STOCKS+['SPY']].pct_change(fill_method=None).dropna()
    figs={}
    fig,ax=plt.subplots(figsize=(12,5)); close[STOCKS+['SPY']].plot(ax=ax)
    ax.set(title='Adjusted historical prices: 2015–2025',ylabel='USD',xlim=(close.index.min(),close.index.max())); figs['historical_prices']=fig
    fig,axes=plt.subplots(3,3,figsize=(12,9))
    for ticker,ax in zip(returns,axes.flat):
        ax.hist(returns[ticker]*100,bins=60); ax.set(title=ticker,xlabel='Daily return (%)',ylabel='Frequency')
    figs['daily_return_distributions']=fig
    fig,ax=plt.subplots(figsize=(10,5)); (returns.std()*np.sqrt(252)*100).sort_values().plot.barh(ax=ax)
    ax.set(title='Annualized historical volatility',xlabel='%'); figs['annualized_volatility']=fig
    fig,ax=plt.subplots(figsize=(9,8)); corr=returns.corr(); image=ax.imshow(corr,vmin=-1,vmax=1,cmap='coolwarm')
    ax.set_xticks(range(len(corr)),corr.columns,rotation=45); ax.set_yticks(range(len(corr)),corr.index)
    for i in range(len(corr)):
        for j in range(len(corr)): ax.text(j,i,f'{corr.iloc[i,j]:.2f}',ha='center',va='center',fontsize=8)
    fig.colorbar(image,ax=ax); ax.set_title('Daily stock return correlations'); figs['return_correlations']=fig
    fig,ax=plt.subplots(figsize=(12,5)); equity.plot(ax=ax)
    ax.set(title='Growth of $100,000: final 2024–2025 test',ylabel='USD',xlim=(equity.index.min(),equity.index.max())); figs['portfolio_100000']=fig
    pooled=importance[(importance.architecture=='pooled')&(importance.group=='A')&(~importance.feature.str.startswith('ticker__'))]
    for task in ['return','risk']:
        fig,axes=plt.subplots(1,2,figsize=(13,6))
        for algorithm,ax in zip(['RF','XGB'],axes):
            top=pooled[(pooled.algorithm==algorithm)&(pooled.task==task)].nlargest(10,'importance')
            ax.barh(top.feature.str.replace('remainder__','',regex=False)[::-1],top.importance[::-1]); ax.set(title=f'{algorithm}: {task}',xlabel='Impurity/gain importance')
        figs['feature_importance_'+task]=fig
    for name,fig in figs.items():
        fig.tight_layout(); fig.savefig(folder/(name+'.png'),dpi=130); plt.close(fig)


def discussion(scores,performance,importance,significance,chosen):
    lines=['# Results and critical discussion','', '## Model comparison']
    for task,metric in [('return','MAE'),('risk','F1')]:
        table=scores[(scores.task==task)&(scores.estimator=='model')]
        winner=table.sort_values(metric,ascending=task=='return').iloc[0]
        lines.append(f"On final test, lowest MAE / highest F1 for {task}: {winner.algorithm}, group {winner.group}, {winner.architecture}; {metric}={winner[metric]:.4f}. This is a descriptive test comparison, not a new model-selection decision.")
        baseline=scores[(scores.task==task)&(scores.estimator=='baseline')]
        lines.append(f"Baseline {metric} range: {baseline[metric].min():.4f}–{baseline[metric].max():.4f}.")
    lines+=['','## Returns versus risk','Return regression and risk classification use different metrics and cannot be ranked by raw percentages. Compare MAE against zero-return MAE and F1/accuracy against majority-class performance. Risk persistence may aid classification while short-horizon return direction remains noisy.','', '## Individual versus pooled']
    for group in ['A','B','C']:
        subset=scores[(scores.group==group)&(scores.task=='return')&(scores.estimator=='model')]
        for algorithm in ['RF','XGB']:
            values=subset[subset.algorithm==algorithm].set_index('architecture').MAE
            lines.append(f"{group}/{algorithm}: pooled MAE {values['pooled']:.4f}, individual MAE {values['individual']:.4f}.")
    spy=float(performance.set_index('strategy').loc['SPY','total_return'])
    lines+=['','## Portfolio results',f'SPY buy-and-hold total return on matching executable dates: {spy:.2%}.']
    for row in performance.itertuples():
        lines.append(f'{row.strategy}: total return {row.total_return:.2%}; annualized {row.annualized_return:.2%}; volatility {row.annualized_volatility:.2%}; Sharpe (cash/risk-free assumed zero) {row.Sharpe_rf_zero:.2f}; maximum drawdown {row.max_drawdown:.2%}; final capital ${row.final_capital:,.2f}.')
    lines+=['Better predictive metrics do not necessarily yield better investment returns: ranking, exposure, errors in selected stocks, turnover and costs alter portfolio outcomes. Portfolio models were selected on 2023 validation, not final returns.','', '## Economic and event significance']
    for row in significance.itertuples():
        lines.append(f'{row.architecture}/{row.algorithm} {row.comparison}: paired MAE improvement {row.mean_MAE_improvement:.6f}; block-bootstrap 95% CI [{row.ci95_low:.6f}, {row.ci95_high:.6f}]; approximate block sign-flip p={row.p_approx:.4f}; positive significant improvement after 12-comparison Bonferroni: {row.significant_bonferroni}.')
    lines+=['The uncertainty analysis aggregates across stocks by date and resamples approximately five-session blocks. It is an approximate test; financial dependence may extend beyond five sessions. A predictive association does not establish a causal impact of tariffs or wars. More features can worsen generalization.','', '## Interpretation']
    for algorithm in ['RF','XGB']:
        imp=importance[(importance.group=='A')&(importance.architecture=='pooled')&(importance.task=='return')&(importance.algorithm==algorithm)]
        lines.append(algorithm+' most important predictors: '+', '.join(imp.nlargest(5,'importance').feature)+'.')
        individual=importance[(importance.group=='A')&(importance.architecture=='individual')&(importance.task=='return')&(importance.algorithm==algorithm)]
        for ticker in STOCKS:
            lines.append(ticker+'/'+algorithm+': '+', '.join(individual[individual.ticker==ticker].nlargest(3,'importance').feature)+'.')
    lines+=['Importance measures are model-internal impurity/gain scores, not causal effects; correlated predictors share or distort their attribution. Ticker one-hot columns in pooled models identify entities and are not additional financial features.','', '## Generalization evidence and limitations',
            'Evidence: purged chronological partitions, earlier walk-forward windows with earlier-only tuning, training-only risk thresholds, identical test dates across algorithms, and zero-return/majority/equal-weight baselines. No SPY or S&P 500 data are supplied to model fitting.',
            'Limitations: eight selected surviving stocks; revised dividend/split-adjusted history; small and retrospectively chosen event catalogue; target dates and transaction outcomes differ; no complete point-in-time CPI/employment dataset; zero interest on cash; no borrow, tax or market-impact model; only one two-year final test. Policy rates represent economic context but do not replace inflation or employment indicators. Non-significant improvements must not be presented as proof that events help.',
            'The test period has now been inspected: future iterations must identify themselves as exploratory and use a fresh holdout or prospective paper trading for confirmatory validation. No 2026 results are used.',
            'The additional minimum is 70%, as updated by the user. Its metric/formula remains undefined: maximum risk accuracy 80.6% exceeds this level, while maximum directional accuracy 58.2% does not. Accuracy, F1 and investment returns must be assessed separately; overall compliance with the minimum is not certified.','', '## AI assistance',
            'AI assisted with organization, code, feature engineering and writing. Verified corrections: removed SPY returns from training features; corrected the academic target to close(t+5)/close(t)-1; separated executable next-open portfolio returns; verified feature invariance to future-price changes and purged temporal boundaries. The student should review the code, independently reproduce these checks, interpret the outputs and describe their own verification before submission.']
    return '\n\n'.join(lines)


def run(project=PROJECT,trees=80):
    project=Path(project); results=project/'04_recursos/v2_results'; results.mkdir(parents=True,exist_ok=True)
    raw,policy,events=load_inputs(project)
    data,feature_ready=engineer(raw,policy,events)
    assert len(TECH)==12 and set(data.ticker)==set(STOCKS)
    assert not any('spy' in x.lower() or 's&p' in x.lower() for columns in GROUPS.values() for x in columns)
    summary,stats,corr=eda_report(raw)
    (results/'EDA_Summary.txt').write_text(summary,encoding='utf-8')
    stats.to_csv(results/'descriptive_statistics.csv'); corr.to_csv(results/'correlations.csv')
    feature_ready.to_csv(project/'02_datos/v2/features_8_stocks.csv.gz',index=False,compression='gzip')
    best,chosen,tuning,walk,validation=develop(data,trees)
    tuning.to_csv(results/'hyperparameter_tuning.csv',index=False); walk.to_csv(results/'walk_forward.csv',index=False)
    # Persist choices before evaluating final test.
    choices={'parameters':{'|'.join(k):v for k,v in best.items()},'selected':{k:list(v) for k,v in chosen.items()},'trees':trees}
    (results/'frozen_choices.json').write_text(json.dumps(choices,indent=2),encoding='utf-8')
    scores,predictions,fitted,importance=evaluate(data,best,trees)
    significance=ablation(predictions)
    equity,performance,trades=simulate(raw,predictions,chosen)
    scores.to_csv(results/'model_metrics.csv',index=False); significance.to_csv(results/'event_significance.csv',index=False)
    performance.to_csv(results/'portfolio_metrics.csv',index=False); equity.to_csv(results/'portfolio_equity.csv')
    trades.to_csv(results/'trades.csv',index=False); importance.to_csv(results/'feature_importance.csv',index=False)
    for key,pred in predictions.items(): pred.to_csv(results/('predictions_'+'_'.join(key)+'.csv.gz'),index=False,compression='gzip')
    joblib.dump({'models':fitted,'validation_models':{},'best':best,'chosen':chosen,'trees':trees},results/'models.joblib')
    figures(raw,equity,importance,project/'03_graficos/v2')
    report=discussion(scores,performance,importance,significance,chosen)
    (results/'DISCUSSION.md').write_text(report,encoding='utf-8')
    print(performance.to_string(index=False),flush=True)
    return dict(raw=raw,data=data,feature_ready=feature_ready,policy=policy,events=events,
                scores=scores,performance=performance,equity=equity,importance=importance,
                significance=significance,chosen=chosen,fitted=fitted,tuning=tuning,walk=walk,report=report)


if __name__=='__main__':
    run()
