import numpy as np
import pandas as pd
from features import STOCKS


def simulate(raw,predictions,chosen,cost_bps=10):
    returns=predictions[chosen['return']].set_index(['date','ticker'])
    risks=predictions[chosen['risk']].set_index(['date','ticker'])
    opens=raw['Open']; index=raw.index
    available=sorted(set(returns.index.get_level_values('date')) & set(risks.index.get_level_values('date')))
    start=index.get_loc(available[0]); signal_dates=index[start::5]
    capitals={name:100000. for name in ['Equal weight','ML top 3','Risk aware ML','SPY']}
    curves=[]; trades=[]; weights={name:{} for name in capitals}; positions={}
    entry_first=index[start+1]; endpoint=None
    for signal in signal_dates:
        if signal not in available: continue
        pos=index.get_loc(signal)
        if pos+6>=len(index): break
        entry,exit=index[pos+1],index[pos+6]
        if exit>=pd.Timestamp('2026-01-01'): break
        p=returns.loc[signal].reindex(STOCKS)
        q=risks.loc[signal].reindex(STOCKS)
        if p.prediction.isna().any() or q.prediction.isna().any(): continue
        top=p.prediction.nlargest(3).index.tolist()
        safe=p.loc[q.prediction.eq(0)].prediction.nlargest(3).index.tolist()
        selections={'Equal weight':STOCKS,'ML top 3':top,'Risk aware ML':safe,'SPY':['SPY']}
        new_weights={}
        for name,selected in selections.items():
            target={t:1/len(selected) for t in selected} if selected else {}
            previous=weights[name]
            # Include explicit cash weight so all-cash to fully invested costs one side.
            turnover=sum(abs(target.get(t,0)-previous.get(t,0)) for t in set(target)|set(previous))
            fee=0. if name=='SPY' else turnover*cost_bps/10000
            before=capitals[name]; capital=before*(1-fee)
            units={t:capital*w/opens.loc[entry,t] for t,w in target.items()}
            cash=capital*(1-sum(target.values()))
            positions[name]=(units,cash)
            trades.append(dict(signal_date=signal,entry_date=entry,exit_date=exit,strategy=name,
                               holdings=', '.join(selected) or 'Cash',turnover=turnover,fee_dollars=before*fee))
            new_weights[name]=target
        if not curves: curves.append(dict(date=entry,**capitals))
        # Daily close mark-to-market and next rebalance open avoid endpoint-only risk metrics.
        for k in range(pos+1,pos+6):
            day=index[k]; row={'date':day}
            for name,(units,cash) in positions.items():
                row[name]=cash+sum(n*raw['Close'].loc[day,t] for t,n in units.items())
            curves.append(row)
        for name,(units,cash) in positions.items():
            capitals[name]=cash+sum(n*opens.loc[exit,t] for t,n in units.items())
            new_weights[name]={t:n*opens.loc[exit,t]/capitals[name] for t,n in units.items()}
        weights=new_weights; endpoint=exit
    if endpoint is None: raise ValueError('Sin periodos ejecutables')
    for name in capitals:
        if name!='SPY': capitals[name]*=1-cost_bps/10000*sum(weights[name].values())
    curves.append(dict(date=endpoint,**capitals))
    equity=pd.DataFrame(curves).set_index('date')
    # Initial 100k row is a distinct observation immediately before first execution.
    equity=equity.loc[~equity.index.duplicated(keep='last')]
    equity=pd.concat([pd.DataFrame({k:[100000.] for k in capitals},index=pd.DatetimeIndex([entry_first-pd.Timedelta(seconds=1)],name='date')),equity])
    rows=[]
    for name in capitals:
        r=equity[name].pct_change().dropna(); years=(equity.index[-1]-equity.index[0]).total_seconds()/86400/365.25
        rows.append(dict(strategy=name,total_return=equity[name].iloc[-1]/100000-1,
                         annualized_return=(equity[name].iloc[-1]/100000)**(1/years)-1,
                         annualized_volatility=float(r.std()*np.sqrt(252)),
                         Sharpe_rf_zero=float(r.mean()/r.std()*np.sqrt(252)) if r.std()>0 else np.nan,
                         max_drawdown=float((equity[name]/equity[name].cummax()-1).min()),final_capital=float(equity[name].iloc[-1])))
    return equity,pd.DataFrame(rows),pd.DataFrame(trades)
