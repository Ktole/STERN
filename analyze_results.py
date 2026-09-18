from pathlib import Path
import pandas as pd, numpy as np
from scipy.stats import t
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'outputs/raw_saa_runs.csv'); x=df.loc[df.success==True,'objective'].dropna().to_numpy(float)
if len(x):
 mean=x.mean(); se=x.std(ddof=1)/np.sqrt(len(x)) if len(x)>1 else 0; q=t.ppf(.975,len(x)-1) if len(x)>1 else 0
 summary=pd.DataFrame([{'n_feasible':len(x),'mean_objective':mean,'sd':x.std(ddof=1) if len(x)>1 else 0,'ci95_low':mean-q*se,'ci95_high':mean+q*se}])
else: summary=pd.DataFrame([{'n_feasible':0,'mean_objective':np.nan,'sd':np.nan,'ci95_low':np.nan,'ci95_high':np.nan}])
summary.to_csv(ROOT/'outputs/analysis_summary.csv',index=False); print(summary.to_string(index=False))
