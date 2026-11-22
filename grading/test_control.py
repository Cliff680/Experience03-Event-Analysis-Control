from src.runtime import Exchange
from src.scenarios import dial,connected
from src.switch_engine import sample_frame,exchange_frame

def test_dial_tone():
    s=Exchange();s.enqueue(0,'OFFHOOK','1001');s.run(0)
    assert s.calls['C1'].state=='COLLECTING' and s.logs[0]['actions'][0]['type']=='DIAL_TONE'
def test_ringing_reserved_no_connection():
    s=Exchange();dial(s);s.run(500)
    assert s.calls['C1'].state=='RINGING' and s.owners['1002']=='C1' and not s.tables.pairs
    assert {a['type'] for a in s.logs[-1]['actions']} >= {'RING','RINGBACK'}
def test_answer_real_bytes():
    s=connected();x=sample_frame(7);y=exchange_frame(x,s.tables)
    assert s.calls['C1'].state=='CONNECTED' and y[0,1]==x[0,2] and y[0,2]==x[0,1]
def test_caller_release():
    s=connected();s.enqueue(1000,'ONHOOK','1001');s.run(1000)
    assert not s.tables.pairs and not s.owners and s.waiting=={'1002'}
def test_callee_release():
    s=connected();s.enqueue(1000,'ONHOOK','1002');s.run(1000)
    assert not s.tables.pairs and s.waiting=={'1001'}
def test_invalid_self():
    for num,why in [('9999','INVALID'),('1001','SELF_CALL')]:
        s=Exchange();dial(s,number=num);s.run(500)
        assert s.calls['C1'].reason==why and not s.tables.pairs and '1001' in s.waiting
def test_busy_preserves_call():
    s=connected();dial(s,'1003','1002',1000);s.run(1500)
    assert s.calls['C2'].reason=='USER_BUSY' and s.calls['C1'].state=='CONNECTED' and len(s.tables.pairs)==1
def test_cancel_ringing():
    s=Exchange();dial(s);s.enqueue(600,'ONHOOK','1001');s.run()
    assert s.calls['C1'].reason=='CALLER_CANCEL' and not s.owners and not s.tables.pairs
def test_network_reject():
    s=Exchange();s.activate=lambda c:False;dial(s);s.enqueue(800,'OFFHOOK','1002');s.run()
    assert s.calls['C1'].reason=='NETWORK_BUSY' and not s.owners and not s.tables.pairs
def test_wait_until_hook_and_reuse():
    s=connected();s.enqueue(1000,'ONHOOK','1001');s.enqueue(1100,'ONHOOK','1002');dial(s,start=1200);s.enqueue(2000,'OFFHOOK','1002');s.run()
    assert len(s.tables.pairs)==1 and s.calls['C2'].state=='CONNECTED' and not s.waiting
