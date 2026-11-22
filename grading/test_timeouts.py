from src.runtime import Exchange
from src.scenarios import dial,connected

def test_dial_timeout():
    s=Exchange();s.enqueue(0,'OFFHOOK','1001');s.run();assert s.calls['C1'].reason=='DIAL_TIMEOUT' and not s.owners
def test_ring_timeout():
    s=Exchange();dial(s);s.run();assert s.calls['C1'].reason=='NO_ANSWER' and not s.owners
def test_old_ring_after_answer():
    s=connected();s.run();assert s.calls['C1'].state=='CONNECTED' and len(s.tables.pairs)==1
def test_old_dial_after_ringing():
    s=Exchange();dial(s);s.run(5000);assert s.calls['C1'].state=='RINGING'
def test_timeout_after_cancel():
    s=Exchange();dial(s);s.enqueue(600,'ONHOOK','1001');s.run();assert s.calls['C1'].reason=='CALLER_CANCEL'
def test_same_time_order():
    s=Exchange();dial(s);s.enqueue(10400,'OFFHOOK','1002');s.run()
    assert s.calls['C1'].state=='CONNECTED'
