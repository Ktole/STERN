"""Scenario-realized time-expanded MILP reference model.
Core logic: route flow, action initiation/completion, OR-of-AND eligibility,
first activation, finite lifetime, and latent-arc usability.
"""
from pathlib import Path
import json, numpy as np, pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix

def solve(benchmark_dir, scenario_df, scenario_id=0, time_limit=30):
    b=Path(benchmark_dir); arcs=pd.read_csv(b/'arcs.csv'); actions=pd.read_csv(b/'actions.csv'); pre=pd.read_csv(b/'prerequisites.csv'); meta=json.loads((b/'metadata.json').read_text())
    sc=scenario_df[scenario_df.scenario_id==scenario_id].set_index('arc_id'); T=int(meta['horizon']); s=int(meta['origin']); d=int(meta['destination'])
    # x[e,t], y[k,t]; core executable model uses action completion to gate latent traversal.
    # OR-of-AND alternatives are encoded directly as linear gates for each candidate latent traversal.
    xkeys=[(int(e),t) for e in arcs.arc_id for t in range(T)]
    ykeys=[(int(k),t) for k in actions.action_id for t in range(T)]
    keys=[('x',)+q for q in xkeys]+[('y',)+q for q in ykeys]; idx={k:i for i,k in enumerate(keys)}; n=len(keys)
    c=np.zeros(n); integ=np.ones(n)
    for _,r in arcs.iterrows():
      e=int(r.arc_id); cost=float(r.mean_cost)*float(sc.loc[e,'travel_factor'])
      for t in range(T): c[idx[('x',e,t)]]=cost
    for _,r in actions.iterrows():
      for t in range(T): c[idx[('y',int(r.action_id),t)]]=float(r.action_cost)
    rows=[]; lo=[]; hi=[]
    # time-expanded unit-travel flow; waiting is implicit through unused epochs, source departs once, destination arrives once
    for v in range(int(arcs[['tail','head']].to_numpy().max())+1):
      for t in range(T+1):
        row={}
        if t<T:
          for e in arcs.loc[arcs['tail']==v,'arc_id']: row[idx[('x',int(e),t)]]=row.get(idx[('x',int(e),t)],0)+1
        if t>0:
          for e in arcs.loc[arcs['head']==v,'arc_id']: row[idx[('x',int(e),t-1)]]=row.get(idx[('x',int(e),t-1)],0)-1
        rhs=1 if (v==s and t==0) else (-1 if (v==d and t==T) else 0)
        # allow destination to hold flow after arrival by enforcing arrival at final epoch via zero-cost self bookkeeping is unavailable;
        # instead constrain aggregate departure/arrival below and skip intermediate d/s balance.
        if v not in (s,d): rows.append(row); lo.append(0); hi.append(0)
    # exactly one departure from s and one arrival to d
    row={idx[('x',int(e),t)]:1 for e in arcs.loc[arcs['tail']==s,'arc_id'] for t in range(T)}; rows.append(row); lo.append(1); hi.append(1)
    row={idx[('x',int(e),t)]:1 for e in arcs.loc[arcs['head']==d,'arc_id'] for t in range(T)}; rows.append(row); lo.append(1); hi.append(1)
    # action at most once
    for k in actions.action_id:
      row={idx[('y',int(k),t)]:1 for t in range(T)}; rows.append(row); lo.append(0); hi.append(1)
    # latent traversal: at least one prerequisite alternative must have all actions completed before t; scenario success required.
    # We implement each OR alternative by auxiliary-free big-M gate: x[e,t] <= sum_r feasible_alt_r(t), where feasible_alt is
    # represented conservatively through action starts. For exact linear OR, add alternative selector variables per traversal.
    # Here selectors are added dynamically.
    # rebuild variable arrays with selectors
    zkeys=[]
    for e in arcs.loc[arcs.latent==1,'arc_id']:
      for t in range(T):
        for r in sorted(pre.loc[pre.latent_arc_id==e,'alternative_id'].unique()): zkeys.append(('z',int(e),t,int(r)))
    oldn=n
    for k in zkeys: idx[k]=len(keys); keys.append(k)
    n=len(keys); c=np.pad(c,(0,n-oldn)); integ=np.ones(n)
    # latent constraints
    for e in arcs.loc[arcs.latent==1,'arc_id']:
      e=int(e); success=int(sc.loc[e,'activation_success']); life=int(sc.loc[e,'lifetime'])
      alts=sorted(pre.loc[pre.latent_arc_id==e,'alternative_id'].unique())
      for t in range(T):
        row={idx[('x',e,t)]:1}
        for r in alts: row[idx[('z',e,t,int(r))]]=row.get(idx[('z',e,t,int(r))],0)-success
        rows.append(row); lo.append(-np.inf); hi.append(0)
        for r in alts:
          ks=pre[(pre.latent_arc_id==e)&(pre.alternative_id==r)].action_id.astype(int).tolist()
          z=idx[('z',e,t,int(r))]
          # z implies every prerequisite action started recently enough to complete and not expire
          for k in ks:
            dur=int(actions.loc[actions.action_id==k,'duration'].iloc[0]); valid=[tau for tau in range(max(0,t-life-dur+1), max(0,t-dur+1))]
            rr={z:1};
            for tau in valid: rr[idx[('y',k,tau)]]=rr.get(idx[('y',k,tau)],0)-1
            rows.append(rr); lo.append(-np.inf); hi.append(0)
    A=lil_matrix((len(rows),n),dtype=float)
    for i,row in enumerate(rows):
      for j,v in row.items(): A[i,j]=v
    res=milp(c,integrality=integ,bounds=Bounds(np.zeros(n),np.ones(n)),constraints=LinearConstraint(A.tocsr(),np.array(lo),np.array(hi)),options={'time_limit':time_limit})
    chosen=[]
    if res.x is not None:
      for e,t in xkeys:
        if res.x[idx[('x',e,t)]]>.5: chosen.append((e,t))
    return {'success':bool(res.success),'status':int(res.status),'objective':None if res.fun is None else float(res.fun),'route_arc_times':chosen,'message':res.message}
