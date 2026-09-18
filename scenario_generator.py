from pathlib import Path
import numpy as np, pandas as pd

def generate(benchmark_dir, cfg, n_scenarios, out_file, seed):
    rng=np.random.default_rng(seed); arcs=pd.read_csv(Path(benchmark_dir)/'arcs.csv'); latent=arcs.loc[arcs.latent==1,'arc_id'].tolist()
    rows=[]
    sigma=(np.log(1+cfg['travel_cv']**2))**0.5; mu=-0.5*sigma*sigma
    for w in range(n_scenarios):
      common=rng.lognormal(mu,sigma)
      for e in arcs.arc_id:
        tf=float(common*rng.lognormal(mu,sigma/2))
        if e in latent:
          success=int(rng.random()<cfg['activation_probability']); life=int(rng.integers(cfg['lifetime_low'],cfg['lifetime_high']+1))
        else: success=1; life=10**6
        rows.append([w,e,tf,success,life])
    df=pd.DataFrame(rows,columns=['scenario_id','arc_id','travel_factor','activation_success','lifetime'])
    Path(out_file).parent.mkdir(parents=True,exist_ok=True); df.to_csv(out_file,index=False); return df
