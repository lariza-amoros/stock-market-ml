import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
from sklearn.metrics import mean_absolute_error,root_mean_squared_error,accuracy_score,precision_score,recall_score,f1_score,roc_auc_score
from sklearn.model_selection import ParameterGrid
from xgboost import XGBRegressor,XGBClassifier
from features import GROUPS,STOCKS,split

SEED=42
GRIDS={'RF':{'max_depth':[3,6],'min_samples_leaf':[10,30]},
       'XGB':{'max_depth':[2,4],'learning_rate':[0.03,0.1]}}


def factory(algorithm,task,params,columns,pooled,trees=80):
    preprocess=ColumnTransformer([('ticker',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['ticker'])],remainder='passthrough') if pooled else 'passthrough'
    common=dict(n_estimators=trees,random_state=SEED,n_jobs=2,**params)
    if algorithm=='RF':
        model=(RandomForestRegressor if task=='return' else RandomForestClassifier)(**common)
    else:
        model=(XGBRegressor if task=='return' else XGBClassifier)(**common,subsample=.8,colsample_bytree=.8)
    return make_pipeline(preprocess,model)


def metrics(task,truth,pred,prob=None):
    if task=='return':
        return {'MAE':mean_absolute_error(truth,pred),'RMSE':root_mean_squared_error(truth,pred),
                'DirectionalAccuracy':float(np.mean((np.asarray(truth)>0)==(np.asarray(pred)>0))),
                'Spearman':float(spearmanr(truth,pred).statistic) if np.std(pred)>0 else np.nan}
    return {'Accuracy':accuracy_score(truth,pred),'Precision':precision_score(truth,pred,zero_division=0),
            'Recall':recall_score(truth,pred,zero_division=0),'F1':f1_score(truth,pred,zero_division=0),
            'ROC_AUC':roc_auc_score(truth,prob) if pd.Series(truth).nunique()==2 else np.nan}


def fit_predict(train,valid,group,algorithm,task,params,architecture,trees=80):
    numeric=GROUPS[group]
    columns=numeric+(['ticker'] if architecture=='pooled' else [])
    bundles={}; rows=[]
    thresholds=train.groupby('ticker').target_volatility.quantile(.75).to_dict()
    entities=['ALL'] if architecture=='pooled' else STOCKS
    for entity in entities:
        tr=train if entity=='ALL' else train[train.ticker==entity]
        va=valid if entity=='ALL' else valid[valid.ticker==entity]
        threshold=thresholds if entity=='ALL' else thresholds[entity]
        y=tr.target_return if task=='return' else (tr.target_volatility>tr.ticker.map(thresholds)).astype(int)
        if task=='risk' and y.nunique()<2: raise ValueError('Faltan clases de riesgo')
        model=factory(algorithm,task,params,columns,entity=='ALL',trees)
        model.fit(tr[columns],y)
        pred=model.predict(va[columns])
        out=va[['date','ticker','target_return','target_volatility','target_end','execution_return','execution_end']].copy()
        out['truth']=va.target_return if task=='return' else (va.target_volatility>va.ticker.map(thresholds)).astype(int)
        out['prediction']=pred
        out['probability']=np.nan if task=='return' else model.predict_proba(va[columns])[:,1]
        # Both baselines use the same rows and partition-specific training only.
        baseline=0. if task=='return' else int(float(y.mean())>=.5)
        out['baseline']=baseline
        out['baseline_probability']=np.nan if task=='return' else float(y.mean())
        rows.append(out)
        bundles[entity]=dict(model=model,columns=columns,threshold=threshold,params=params)
    return pd.concat(rows).sort_values(['date','ticker']),bundles


def develop(data,trees=80):
    train,val=split(data,'2023-01-01','2024-01-01')
    records=[]; best={}; validation={}; walk=[]
    # All configurations and model selection use pre-2024 rows only.
    for group in ['A','B','C']:
        for architecture in ['pooled','individual']:
            for algorithm in ['RF','XGB']:
                for task in ['return','risk']:
                    key=(group,architecture,algorithm,task)
                    candidates=[]
                    for params in ParameterGrid(GRIDS[algorithm]):
                        pred,_=fit_predict(train,val,*[group,algorithm,task,params,architecture],trees=trees)
                        score=metrics(task,pred.truth,pred.prediction,pred.probability)
                        candidates.append((score['MAE'] if task=='return' else -score['F1'],params,pred))
                        records.append(dict(group=group,architecture=architecture,algorithm=algorithm,task=task,
                                            partition='validation2023',parameters=json.dumps(params),**score))
                    _,params,pred=min(candidates,key=lambda x:x[0])
                    best[key]=params; validation[key]=pred
                    print('Tuned',key,params,flush=True)
        # Rolling checks of winners on two earlier, purged windows.
        for year in [2021,2022]:
            tr,va=split(data,f'{year}-01-01',f'{year+1}-01-01')
            for algorithm in ['RF','XGB']:
                for task in ['return','risk']:
                    tune_train,tune_valid=split(data,f'{year-1}-01-01',f'{year}-01-01')
                    local=[]
                    for candidate in ParameterGrid(GRIDS[algorithm]):
                        check,_=fit_predict(tune_train,tune_valid,group,algorithm,task,candidate,'pooled',trees)
                        m=metrics(task,check.truth,check.prediction,check.probability)
                        local.append((m['MAE'] if task=='return' else -m['F1'],candidate))
                    params=min(local,key=lambda x:x[0])[1]
                    pred,_=fit_predict(tr,va,group,algorithm,task,params,'pooled',trees)
                    walk.append(dict(group=group,year=year,algorithm=algorithm,task=task,
                                     role='chronological walk-forward with earlier tuning',**metrics(task,pred.truth,pred.prediction,pred.probability)))
    chosen={}
    for task in ['return','risk']:
        keys=[k for k in validation if k[3]==task]
        chosen[task]=min(keys,key=lambda k:metrics(task,validation[k].truth,validation[k].prediction,validation[k].probability)['MAE'] if task=='return' else -metrics(task,validation[k].truth,validation[k].prediction,validation[k].probability)['F1'])
    return best,chosen,pd.DataFrame(records),pd.DataFrame(walk),validation


def evaluate(data,best,trees=80):
    train,test=split(data,'2024-01-01','2026-01-01')
    scores=[]; predictions={}; fitted={}; importance=[]
    for key,params in best.items():
        group,architecture,algorithm,task=key
        pred,bundle=fit_predict(train,test,group,algorithm,task,params,architecture,trees)
        predictions[key]=pred; fitted[key]=bundle
        for label in ['model','baseline']:
            truth=pred.truth
            values=pred.prediction if label=='model' else pred.baseline
            prob=pred.probability if label=='model' else pred.baseline_probability
            scores.append(dict(group=group,architecture=architecture,algorithm=algorithm,task=task,
                               estimator=label,partition='test2024_2025',**metrics(task,truth,values,prob)))
        for entity,info in bundle.items():
            pipeline=info['model']; estimator=pipeline.steps[-1][1]
            transformer=pipeline.steps[0][1]
            names=transformer.get_feature_names_out() if architecture=='pooled' else info['columns']
            for name,value in zip(names,estimator.feature_importances_):
                importance.append(dict(group=group,architecture=architecture,algorithm=algorithm,task=task,
                                       ticker=entity,feature=str(name),importance=float(value)))
        print('Test evaluated',key,flush=True)
    return pd.DataFrame(scores),predictions,fitted,pd.DataFrame(importance)


def ablation(predictions):
    rng=np.random.default_rng(SEED); results=[]
    for architecture in ['pooled','individual']:
        for algorithm in ['RF','XGB']:
            for left,right in [('A','B'),('B','C'),('A','C')]:
                a=predictions[(left,architecture,algorithm,'return')].set_index(['date','ticker'])
                b=predictions[(right,architecture,algorithm,'return')].set_index(['date','ticker'])
                joined=a[['truth','prediction']].join(b.prediction.rename('prediction_b'),how='inner')
                improvement=(abs(joined.truth-joined.prediction)-abs(joined.truth-joined.prediction_b)).groupby('date').mean()
                # Five-day blocks reduce dependence from overlapping targets; not IID rows.
                blocks=np.array([x.mean() for x in np.array_split(improvement.to_numpy(),max(1,len(improvement)//5))])
                samples=rng.choice(blocks,size=(2000,len(blocks)),replace=True).mean(axis=1)
                lo,hi=np.quantile(samples,[.025,.975])
                null=(rng.choice([-1,1],size=(2000,len(blocks)))*blocks).mean(axis=1)
                p=(np.sum(abs(null)>=abs(blocks.mean()))+1)/2001
                results.append(dict(architecture=architecture,algorithm=algorithm,comparison=left+'→'+right,
                                    mean_MAE_improvement=float(improvement.mean()),ci95_low=float(lo),ci95_high=float(hi),
                                    p_approx=float(p),significant_bonferroni=bool(p<.05/12 and lo>0)))
    return pd.DataFrame(results)
