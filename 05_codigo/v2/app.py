import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import joblib
import pandas as pd
import streamlit as st
from features import PROJECT,STOCKS,GROUPS,load_inputs,engineer

st.set_page_config(page_title='Stock market · Demo',layout='wide')
st.title('Stock market · Predicciones y cartera demo')
st.caption('Datos 2015–2025 · Modelos entrenados antes de 2024 · SPY solo como referencia')
st.session_state.setdefault('demo_trades',[])


@st.cache_resource(max_entries=1)
def load_models():
    return joblib.load(PROJECT/'04_recursos/v2_results/models.joblib')


@st.cache_data(max_entries=1)
def load_data():
    raw,policy,events=load_inputs()
    data,ready=engineer(raw,policy,events)
    scores=pd.read_csv(PROJECT/'04_recursos/v2_results/model_metrics.csv')
    performance=pd.read_csv(PROJECT/'04_recursos/v2_results/portfolio_metrics.csv')
    equity=pd.read_csv(PROJECT/'04_recursos/v2_results/portfolio_equity.csv',index_col=0,parse_dates=True)
    return raw,ready,scores,performance,equity


def forecast(rows,bundle,key):
    predictions=[]
    for row in rows.itertuples():
        info=bundle['ALL'] if key[1]=='pooled' else bundle[row.ticker]
        frame=rows[rows.ticker.eq(row.ticker)]
        estimate=float(info['model'].predict(frame[info['columns']])[0])
        risk=None if key[3]=='return' else float(info['model'].predict_proba(frame[info['columns']])[0,1])
        predictions.append(dict(ticker=row.ticker,estimate=estimate,risk=risk))
    return pd.DataFrame(predictions).set_index('ticker')


try:
    bundle=load_models(); raw,ready,scores,performance,equity=load_data()
except (FileNotFoundError,ImportError) as error:
    st.error('Faltan los resultados del notebook. Ejecuta primero el experimento o usa el paquete completo generado.')
    st.stop()

predict,results,demo=st.tabs(['Predicciones','Resultados','Cuenta demo'])
with predict:
    st.write('Replay histórico: elige una fecha y compara pronósticos a cinco sesiones. Los modelos no se reentrenan con los resultados de esa fecha.')
    dates=[d.date() for d in raw.index if pd.Timestamp('2024-01-01')<=d<=raw.index[-7]]
    with st.form('predict'):
        date=st.selectbox('Fecha de señal',dates,index=len(dates)-1)
        group=st.selectbox('Variables',['A','B','C'],format_func=lambda x:{'A':'12 técnicas','B':'Técnicas + VIX y política económica','C':'Anteriores + eventos'}[x])
        architecture=st.selectbox('Enfoque',['pooled','individual'])
        algorithm=st.selectbox('Algoritmo',['RF','XGB'])
        submit=st.form_submit_button('Calcular pronósticos',type='primary')
    if submit:
        rows=ready[ready.date.eq(pd.Timestamp(date))]
        key=(group,architecture,algorithm,'return')
        ret=forecast(rows,bundle['models'][key],key)
        risk=forecast(rows,bundle['models'][(group,architecture,algorithm,'risk')],(group,architecture,algorithm,'risk'))
        display=pd.DataFrame({'Acción':ret.index,'Retorno previsto (%)':ret.estimate.to_numpy()*100,
                              'Riesgo alto (%)':risk.risk.reindex(ret.index).to_numpy()*100})
        display['Cierre de señal']=raw['Close'].loc[pd.Timestamp(date),display['Acción']].to_numpy()
        display['Cierre previsto a 5 sesiones']=display['Cierre de señal']*(1+display['Retorno previsto (%)']/100)
        st.session_state['forecast']={'date':pd.Timestamp(date),'table':display,'key':key}
    if 'forecast' in st.session_state:
        saved=st.session_state['forecast']
        st.caption(f"Pronóstico guardado para {saved['date']:%Y-%m-%d}; {saved['key'][:3]}")
        st.dataframe(saved['table'],hide_index=True,alt='Pronósticos por acción')
        if st.checkbox('Revelar resultados históricos a cinco sesiones'):
            pos=raw.index.get_loc(saved['date']); exit=raw.index[pos+5]
            actual=raw['Close'].loc[exit,STOCKS]/raw['Close'].loc[saved['date'],STOCKS]-1
            st.dataframe((actual*100).rename('Retorno real (%)'),alt='Resultados históricos posteriores a la señal')
        st.caption('Es una predicción histórica fuera de muestra; el cierre previsto no garantiza un precio ejecutable ni constituye una predicción verificada de 2026.')
with results:
    st.line_chart(equity,alt='Crecimiento de 100 mil dólares en las cuatro estrategias')
    st.dataframe(performance,hide_index=True,alt='Rentabilidad y riesgo de carteras')
    st.dataframe(scores,hide_index=True,alt='Métricas de los modelos y baselines')
with demo:
    st.subheader('Simulador local de operaciones')
    st.write('Capital inicial: $100,000. Sin conexión a un bróker. Cada operación se ejecuta virtualmente en la apertura siguiente y se liquida cinco sesiones después. Coste: 10 puntos básicos por lado.')
    balance=100000+sum(t['profit'] for t in st.session_state.demo_trades)
    st.metric('Capital demo',f'${balance:,.2f}')
    if 'forecast' not in st.session_state:
        st.info('Calcula primero un pronóstico en la pestaña Predicciones.')
    else:
        saved=st.session_state.forecast
        with st.form('trade'):
            ticker=st.selectbox('Acción',STOCKS)
            allocation=st.number_input('Capital para la operación',min_value=0.,max_value=float(max(balance,0)),value=float(min(10000,max(balance,0))),step=1000.)
            trade=st.form_submit_button('Simular operación de cinco sesiones')
        if trade:
            pos=raw.index.get_loc(saved['date']); enter=raw.index[pos+1]; exit=raw.index[pos+6]
            records=st.session_state.demo_trades
            if records and enter<=max(r['exit'] for r in records):
                st.error('Elige una fecha posterior a la última liquidación para evitar reutilizar capital futuro.')
            elif allocation<=0 or allocation>balance:
                st.error('Importe inválido.')
            else:
                entry=float(raw['Open'].loc[enter,ticker]); ending=float(raw['Open'].loc[exit,ticker])
                invested=allocation*(1-.001); units=invested/entry; proceeds=units*ending*(1-.001)
                profit=proceeds-allocation
                records.append(dict(ticker=ticker,signal=saved['date'],entry=enter,exit=exit,capital=allocation,profit=profit,shares=units))
                st.success(f'Operación simulada: resultado ${profit:,.2f}; capital tras liquidación ${balance+profit:,.2f}.')
        if st.session_state.demo_trades:
            ledger=pd.DataFrame(st.session_state.demo_trades)
            st.dataframe(ledger,hide_index=True,alt='Historial de operaciones simuladas')
            st.download_button('Descargar historial',ledger.to_csv(index=False).encode(),'demo_trades.csv','text/csv')
    if st.button('Reiniciar cuenta demo'):
        st.session_state.demo_trades=[]
        st.rerun()
