from pathlib import Path
import numpy as np
import pandas as pd

STOCKS = ['AAPL','MSFT','NVDA','AMZN','GOOGL','JPM','XOM','JNJ']
TECH = ['return_1','return_5','return_10','return_20','ma5_ratio','ma20_ratio',
        'volatility_5','volatility_20','volume_change','volume_ratio20','rsi14','macd_ratio']
MACRO = ['vix','fed_upper','fed_change20','days_since_policy']
EVENT = ['tariff_count20','health_count20','war_count20']
GROUPS = {'A': TECH, 'B': TECH+MACRO, 'C': TECH+MACRO+EVENT}
PROJECT = Path(__file__).resolve().parents[2]


def load_inputs(project=PROJECT):
    folder = project / '02_datos/v2'
    raw = pd.read_csv(folder/'precios_yfinance.csv.gz', header=[0,1], index_col=0, parse_dates=True)
    policy = pd.read_csv(folder/'fed_policy.csv', parse_dates=['date'])
    events = pd.read_csv(folder/'events.csv', parse_dates=['date'])
    assert raw.index.min() >= pd.Timestamp('2015-01-01')
    assert raw.index.max() < pd.Timestamp('2026-01-01')
    assert not raw.isna().any().any()
    assert events.date.max() < pd.Timestamp('2026-01-01')
    return raw, policy, events


def context(index, policy, events, vix):
    out = pd.DataFrame(index=index)
    # Use next observed session after the source date: no announcement-time guessing.
    changes = pd.Series(0., index=index)
    rate = pd.Series(np.nan, index=index)
    last_change = pd.Series(pd.NaT, index=index, dtype='datetime64[ns]')
    rate.iloc[0] = float(policy.iloc[0].rate_upper)
    last_change.iloc[0] = index[0]
    for row in policy.itertuples():
        pos = index.searchsorted(row.date, side='right')
        if pos < len(index):
            rate.iloc[pos] = row.rate_upper
            changes.iloc[pos] += row.change_bps / 100
            last_change.iloc[pos] = index[pos]
    out['vix'] = vix
    out['fed_upper'] = rate.ffill()
    out['fed_change20'] = changes.rolling(20, min_periods=1).sum()
    out['days_since_policy'] = (pd.Series(index,index=index)-last_change.ffill()).dt.days
    for kind in ['tariff','health','war']:
        impulses = pd.Series(0.,index=index)
        for date in events.loc[events.category==kind,'date']:
            pos=index.searchsorted(date,side='right')
            if pos < len(index): impulses.iloc[pos] += 1
        out[kind+'_count20'] = impulses.rolling(20,min_periods=1).sum()
    return out


def engineer(raw, policy, events):
    close, volume, opens = raw['Close'], raw['Volume'], raw['Open']
    ctx = context(raw.index, policy, events, close['^VIX'])
    dates=pd.Series(raw.index,index=raw.index)
    frames=[]
    for ticker in STOCKS:
        p,v=close[ticker],volume[ticker]
        r=p.pct_change(fill_method=None)
        f=pd.DataFrame(index=raw.index)
        for lag in [1,5,10,20]: f[f'return_{lag}']=p.pct_change(lag,fill_method=None)
        for window in [5,20]:
            f[f'ma{window}_ratio']=p/p.rolling(window).mean()-1
            f[f'volatility_{window}']=r.rolling(window).std()
        f['volume_change']=v.pct_change(fill_method=None)
        f['volume_ratio20']=v/v.rolling(20).mean()
        delta=p.diff(); gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False,min_periods=14).mean()
        loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False,min_periods=14).mean()
        f['rsi14']=100-100/(1+gain/loss.replace(0,np.nan))
        f['rsi14']=f.rsi14.where(loss.ne(0),100).where(gain.ne(0)|loss.ne(0),50)
        f['macd_ratio']=(p.ewm(span=12,adjust=False).mean()-p.ewm(span=26,adjust=False).mean())/p
        f=f.join(ctx)
        f['ticker']=ticker
        f['target_return']=p.shift(-5)/p-1
        future=pd.concat([r.shift(-k) for k in range(1,6)],axis=1)
        f['target_volatility']=future.std(axis=1)*np.sqrt(252)
        f['target_end']=dates.shift(-5)
        f['execution_return']=opens[ticker].shift(-6)/opens[ticker].shift(-1)-1
        f['execution_end']=dates.shift(-6)
        f.index.name='date'
        frames.append(f.reset_index())
    all_rows=pd.concat(frames,ignore_index=True).replace([np.inf,-np.inf],np.nan)
    feature_ready=all_rows.dropna(subset=GROUPS['C']).sort_values(['date','ticker'])
    labelled=feature_ready.dropna(subset=['target_return','target_volatility','target_end','execution_return','execution_end']).copy()
    return labelled, feature_ready


def split(data, start, end):
    train=data[(data.date < start)&(data.target_end < start)].copy()
    valid=data[(data.date >= start)&(data.date < end)&(data.target_end < end)].copy()
    if train.empty or valid.empty: raise ValueError('Partición temporal vacía')
    assert train.target_end.max() < valid.date.min()
    return train,valid
