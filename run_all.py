from pathlib import Path
import sys,json,pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from benchmark_generator import generate as gen_bench
from scenario_generator import generate as gen_scen
from saa_simopt import run as run_saa

def main():
 cfg=json.loads((ROOT/'config/experiment.json').read_text()); seed=cfg['master_seed']
 bdir=ROOT/'data/benchmarks/B001'; gen_bench(cfg['benchmark'],bdir,seed)
 total=cfg['saa']['replications']*cfg['saa']['sample_size']+cfg['saa']['validation_size']+cfg['saa']['test_size']
 sdf=gen_scen(bdir,cfg['scenarios'],total,ROOT/'data/scenarios/all_scenarios.csv',seed+1)
 cand=run_saa(bdir,sdf,cfg['saa'],ROOT/'outputs')
 manifest={'version':cfg['version'],'master_seed':seed,'n_scenarios':total,'candidate_count':len(cand)}
 (ROOT/'outputs/run_manifest.json').write_text(json.dumps(manifest,indent=2))
 print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()
