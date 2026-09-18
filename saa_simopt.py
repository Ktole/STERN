from pathlib import Path
import json, numpy as np, pandas as pd
from milp_model import solve

def run(benchmark_dir, scenarios_df, cfg, outdir):
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True); M=cfg['replications']; N=cfg['sample_size']
    raw=[]; candidates=[]
    # Replicated SAA prototype: solve realized MILPs on each optimization batch and retain the best feasible policy signature.
    for m in range(M):
      ids=list(range(m*N,(m+1)*N)); sols=[]
      for sid in ids:
        r=solve(benchmark_dir,scenarios_df,sid); r.update(replication=m,scenario_id=sid); raw.append(r); sols.append(r)
      feasible=[r for r in sols if r['success'] and r['objective'] is not None]
      if feasible: candidates.append(min(feasible,key=lambda r:r['objective']))
    pd.DataFrame(raw).to_csv(out/'raw_saa_runs.csv',index=False)
    pd.DataFrame(candidates).to_csv(out/'candidate_policies.csv',index=False)
    return candidates
