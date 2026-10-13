from pathlib import Path
import sys
import joblib
import pandas as pd
import streamlit as st

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'05_codigo/v2'))
from features import STOCKS,load_inputs,engineer

st.set_page_config(page_title='Stock market ML',page_icon=':material/finance:',layout='wide')
st.title('Can Machine Learning Beat the Stock Market?')
st.caption('Proyecto histórico 2015–2025 · Pronósticos a cinco sesiones · Modelo original')
st.session_state.setdefault('ledger',[])

@st.cache_resource
def resources():
    return joblib.load(ROOT/'04_recursos/v2_results/models.joblib')

@st.cache_data
def inputs():
    raw,policy,events=load_inputs(ROOT)
    _,ready=engineer(raw,policy,events)
    results=ROOT/'04_recursos/v2_results'
    return raw,ready,pd.read_csv(results/'portfolio_metrics.csv'),pd.read_csv(results/'model_metrics.csv'),pd.read_csv(results/'portfolio_equity.csv',index_col=0,parse_dates=True)

def official_forecast(rows,models):
    table=rows[['ticker']].set_index('ticker').copy()
    for task,column in [('return','return'),('risk','risk')]:
        key=tuple(models['chosen'][task]); bundles=models['models'][key]; values={}
        for ticker in STOCKS:
            info=bundles['ALL'] if key[1]=='pooled' else bundles[ticker]
            X=rows[rows.ticker.eq(ticker)][info['columns']]
            values[ticker]=float(info['model'].predict(X)[0]) if task=='return' else float(info['model'].predict_proba(X)[0,1])
        table[column]=pd.Series(values)
    return table.sort_values('return',ascending=False)

try:
    model=resources(); raw,ready,performance,scores,equity=inputs()
except (FileNotFoundError,ImportError) as exc:
    st.error('Faltan datos o modelos de la entrega. Revisa que el repositorio esté completo y las dependencias instaladas.')
    st.stop()

with st.sidebar:
    st.header('Modelo de entrega')
    st.write('XGBoost: retorno agrupado y riesgo individual por acción.')
    st.caption('Entrenamiento anterior a 2024. SPY solo sirve como referencia. Cuenta demo histórica, sin dinero real ni bróker.')
    st.link_button('Notebook', 'https://github.com/lariza-amoros/stock-market-ml/blob/main/01_notebooks/stock_market_proyecto_organizado.ipynb')
    st.link_button('Informe completo','https://github.com/lariza-amoros/stock-market-ml/blob/main/04_recursos/v2_results/INFORME_COMPLETO_PROYECTO.md')

predict,results,demo=st.tabs(['Predicciones','Resultados','Cuenta demo'])
with predict:
    dates=sorted(ready.loc[ready.date.between('2024-01-01',raw.index[-7]),'date'].unique())
    with st.form('forecast_form'):
        date=st.selectbox('Fecha de señal',dates,index=len(dates)-1,format_func=lambda d:pd.Timestamp(d).strftime('%Y-%m-%d'))
        submitted=st.form_submit_button('Calcular pronósticos',type='primary')
    if submitted:
        date=pd.Timestamp(date)
        forecast=official_forecast(ready[ready.date.eq(date)],model)
        st.session_state['forecast']={'date':date,'table':forecast}
    if 'forecast' in st.session_state:
        saved=st.session_state.forecast; table=saved['table']; date=saved['date']; pos=raw.index.get_loc(date)
        st.subheader(f'Pronóstico al cierre del {date:%Y-%m-%d}')
        display=pd.DataFrame({'Acción':table.index,'Retorno previsto (%)':100*table['return'].to_numpy(),
                              'Puntaje de alto riesgo (%)':100*table.risk.to_numpy()})
        st.dataframe(display,hide_index=True,alt='Pronósticos originales de retorno y alto riesgo para ocho acciones')
        st.write('Top 3:',', '.join(table.head(3).index))
        st.caption('El riesgo se refiere a volatilidad, no a probabilidad de perder dinero. Las probabilidades no están calibradas.')
        if st.checkbox('Revelar resultado histórico posterior'):
            actual=raw['Close'].loc[raw.index[pos+5],STOCKS]/raw['Close'].loc[date,STOCKS]-1
            comparison=display.set_index('Acción').join((100*actual).rename('Retorno real (%)'))
            st.dataframe(comparison,alt='Comparación de pronóstico y retorno histórico a cinco cierres')
        st.download_button('Descargar pronósticos',display.to_csv(index=False).encode(),'predicciones.csv','text/csv')
    else:
        st.info('Elige una sesión de 2024 o 2025 para consultar sus ocho pronósticos históricos.')

with results:
    with st.container(horizontal=True):
        st.metric('Dirección del modelo oficial','58.17%',border=True)
        st.metric('F1 de riesgo oficial','29.15%',border=True)
        st.metric('Retorno histórico ML top 3','126.06%',border=True)
    st.caption('Resultados 2024–2025. Rentabilidad y exactitud son métricas diferentes. El mínimo adicional de 70% no se alcanza en dirección.')
    st.line_chart(equity,alt='Capital de cien mil dólares bajo las cuatro estrategias originales')
    display=performance.copy()
    for column in ['total_return','annualized_return','annualized_volatility','max_drawdown']:
        display[column]*=100
    display=display.rename(columns={'total_return':'Retorno (%)','annualized_return':'Retorno anualizado (%)',
        'annualized_volatility':'Volatilidad anualizada (%)','max_drawdown':'Drawdown (%)','Sharpe_rf_zero':'Sharpe (rf=0)','strategy':'Estrategia','final_capital':'Capital final ($)'})
    st.dataframe(display,hide_index=True,alt='Rendimiento y riesgo de las cuatro carteras')
    with st.expander('Métricas de todos los modelos'):
        st.dataframe(scores,hide_index=True,alt='Métricas originales de modelos y baselines; accuracy en escala cero a uno')
    st.caption('Simulación después de costos supuestos de 10 bps por lado. No garantiza resultados futuros.')

with demo:
    st.subheader('Cuenta demo histórica')
    balance=100000.+sum(t['pnl'] for t in st.session_state.ledger)
    st.metric('Capital virtual',f'${balance:,.2f}',border=True)
    if 'forecast' not in st.session_state:
        st.info('Calcula primero un pronóstico en la pestaña Predicciones.')
    else:
        saved=st.session_state.forecast; table=saved['table']; pos=raw.index.get_loc(saved['date'])
        with st.form('demo'):
            strategy=st.selectbox('Estrategia',['ML top 3','Risk aware ML'])
            allocation=st.number_input('Capital para la operación ($)',min_value=0.,max_value=float(max(0,balance)),
                value=float(min(10000,max(0,balance))),step=1000.)
            execute=st.form_submit_button('Simular operación de cinco sesiones')
        if execute:
            entry,exit=raw.index[pos+1],raw.index[pos+6]
            records=st.session_state.ledger
            selected=table.head(3).index.tolist() if strategy=='ML top 3' else table[table.risk<.5].head(3).index.tolist()
            if records and entry<=max(t['exit'] for t in records):
                st.error('Elige una fecha posterior a la última liquidación para evitar reutilizar capital futuro.')
            elif allocation<=0 or allocation>balance:
                st.error('Selecciona un importe válido.')
            elif not selected:
                st.info('No hay acciones elegibles: el capital permanece en efectivo.')
            else:
                shares={t:allocation*.999/len(selected)/raw['Open'].loc[entry,t] for t in selected}
                proceeds=sum(n*raw['Open'].loc[exit,t] for t,n in shares.items())*.999
                pnl=float(proceeds-allocation)
                records.append(dict(strategy=strategy,holdings=', '.join(selected),signal=saved['date'],entry=entry,exit=exit,allocation=allocation,pnl=pnl))
                st.success(f'Resultado neto: ${pnl:,.2f}. Capital después de liquidar: ${balance+pnl:,.2f}.')
        st.caption('Compra en la apertura siguiente y venta cinco sesiones después. Cada operación demo paga 10 bps por lado; no reproduce el turnover completo de una cartera continua.')
    if st.session_state.ledger:
        ledger=pd.DataFrame(st.session_state.ledger)
        st.dataframe(ledger,hide_index=True,alt='Historial de carteras simuladas y resultados netos')
        st.download_button('Descargar historial',ledger.to_csv(index=False).encode(),'cuenta_demo.csv','text/csv')
    if st.button('Reiniciar cuenta demo'):
        st.session_state.ledger=[]
        st.rerun()
