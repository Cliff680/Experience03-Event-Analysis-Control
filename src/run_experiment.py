"""生成场景判定、完整过程日志和状态时序图。"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.scenarios import run_scenarios

def main():
    dest=Path('results');dest.mkdir(exist_ok=True)
    results,logs=run_scenarios()
    (dest/'scenario_results.json').write_text(json.dumps({'scenarios':results,'passed':sum(x['passed'] for x in results),'total':len(results)},ensure_ascii=False,indent=2),encoding='utf-8')
    (dest/'call_events.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in logs),encoding='utf-8')
    fig,axes=plt.subplots(2,1,figsize=(10,6),layout='constrained')
    states=['IDLE','COLLECTING','RINGING','CONNECTED','ENDED']
    for ax,name in zip(axes,['release_1001','NO_ANSWER']):
        rows=[x for x in logs if x['scenario']==name and x['call_id']=='C1']
        ax.step([x['time_ms'] for x in rows],[states.index(x['after']) for x in rows],where='post',marker='o')
        ax.set(yticks=range(5),yticklabels=states,xlabel='Simulation time (ms)',title=name);ax.grid(alpha=.3)
    fig.savefig(dest/'call_sequence.png',dpi=160);plt.close(fig)
    print(f"Scenarios passed: {sum(x['passed'] for x in results)}/{len(results)}")
    if not all(x['passed'] for x in results):raise SystemExit('存在未通过场景，请检查JSON和日志')
if __name__=='__main__':main()
