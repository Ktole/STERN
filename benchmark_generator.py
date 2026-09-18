from pathlib import Path
import json, math
import numpy as np
import pandas as pd

def generate(cfg, outdir, seed):
    rng=np.random.default_rng(seed); n=cfg['n_nodes']; out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    xy=rng.uniform(0,100,(n,2)); nodes=pd.DataFrame({'node_id':range(n),'x':xy[:,0],'y':xy[:,1],'is_origin':[1]+[0]*(n-1),'is_destination':[0]*(n-1)+[1]})
    arcs=[]; aid=0
    # guaranteed bidirectional chain
    pairs=set()
    for i in range(n-1): pairs|={(i,i+1),(i+1,i)}
    for i in range(n):
      for j in range(n):
        if i!=j and rng.random()<cfg['base_arc_probability']: pairs.add((i,j))
    def dist(i,j): return float(np.linalg.norm(xy[i]-xy[j])/10+1)
    for i,j in sorted(pairs): arcs.append([aid,i,j,dist(i,j),0]); aid+=1
    existing=set(pairs); latent=[]
    candidates=[(i,j) for i in range(n) for j in range(n) if i!=j and (i,j) not in existing]
    rng.shuffle(candidates)
    for i,j in candidates[:cfg['n_latent']]: latent.append(aid); arcs.append([aid,i,j,0.65*dist(i,j),1]); aid+=1
    actions=pd.DataFrame({'action_id':range(cfg['n_actions']),'location':rng.integers(0,n-1,cfg['n_actions']),'action_cost':rng.uniform(1,4,cfg['n_actions']).round(3),'duration':rng.integers(1,3,cfg['n_actions'])})
    prereq=[]
    for e in latent:
      # one or two OR alternatives; each alternative has 1-2 actions
      for r in range(int(rng.integers(1,3))):
        ks=rng.choice(cfg['n_actions'],size=int(rng.integers(1,min(3,cfg['n_actions']+1))),replace=False)
        for k in ks: prereq.append([e,r,int(k)])
    pd.DataFrame(arcs,columns=['arc_id','tail','head','mean_cost','latent']).to_csv(out/'arcs.csv',index=False)
    nodes.to_csv(out/'nodes.csv',index=False); actions.to_csv(out/'actions.csv',index=False)
    pd.DataFrame(prereq,columns=['latent_arc_id','alternative_id','action_id']).to_csv(out/'prerequisites.csv',index=False)
    meta={'seed':seed,'horizon':cfg['horizon'],'origin':0,'destination':n-1}
    (out/'metadata.json').write_text(json.dumps(meta,indent=2))
    return out
