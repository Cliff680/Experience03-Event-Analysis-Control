import json
from pathlib import Path
from src.scenarios import run_scenarios

def test_twelve_scenarios():
    results,logs=run_scenarios();assert len(results)==12 and all(x['passed'] for x in results)
def test_saved_results_match_execution():
    actual,_=run_scenarios();data=json.loads(Path('results/scenario_results.json').read_text(encoding='utf-8'))
    assert data=={'scenarios':actual,'passed':12,'total':12}
def test_saved_events_match_execution():
    _,logs=run_scenarios();saved=[json.loads(x) for x in Path('results/call_events.jsonl').read_text(encoding='utf-8').splitlines()]
    assert saved==logs
def test_result_image():
    from PIL import Image
    with Image.open('results/call_sequence.png') as im:im.verify()
    assert Path('results/call_sequence.png').stat().st_size>1000
