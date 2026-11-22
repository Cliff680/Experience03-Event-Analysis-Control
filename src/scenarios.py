"""教师固定场景，用逻辑时间代替等待真实秒数。"""
from src.runtime import Exchange
from src.switch_engine import sample_frame,exchange_frame

def dial(s,caller='1001',number='1002',start=0):
    s.enqueue(start,'OFFHOOK',caller)
    for i,d in enumerate(number):s.enqueue(start+100*(i+1),'DIGIT',caller,d)

def connected():
    s=Exchange();dial(s);s.enqueue(800,'OFFHOOK','1002');s.run(900);return s

def run_scenarios():
    results=[];logs=[]
    def add(name,ok,s):
        results.append({'scenario':name,'passed':bool(ok)});logs.extend(dict(row,scenario=name) for row in s.logs)
    s=connected();a=sample_frame(0);out=exchange_frame(a,s.tables)
    add('normal_bidirectional',s.calls['C1'].state=='CONNECTED' and out[0,1]==a[0,2] and out[0,2]==a[0,1],s)
    for who in ['1001','1002']:
        s=connected();s.enqueue(1000,'ONHOOK',who);s.run();other='1002' if who=='1001' else '1001'
        add('release_'+who,not s.tables.pairs and other in s.waiting and who not in s.waiting,s)
    for number,reason in [('9999','INVALID'),('1001','SELF_CALL')]:
        s=Exchange();dial(s,number=number);s.run();add(reason,s.calls['C1'].reason==reason and not s.tables.pairs,s)
    s=connected();dial(s,'1003','1002',1000);s.run();add('USER_BUSY',s.calls['C2'].reason=='USER_BUSY' and s.calls['C1'].state=='CONNECTED',s)
    s=Exchange();s.enqueue(0,'OFFHOOK','1001');s.run();add('DIAL_TIMEOUT',s.calls['C1'].reason=='DIAL_TIMEOUT' and not s.owners,s)
    s=Exchange();dial(s);s.run();add('NO_ANSWER',s.calls['C1'].reason=='NO_ANSWER' and not s.owners,s)
    s=Exchange();dial(s);s.enqueue(600,'ONHOOK','1001');s.run();add('cancel_ringing',s.calls['C1'].reason=='CALLER_CANCEL' and not s.owners,s)
    s=connected();s.run();add('stale_timer',s.calls['C1'].state=='CONNECTED' and len(s.tables.pairs)==1,s)
    s=Exchange();s.enqueue(0,'OFFHOOK','1001');s.enqueue(1,'OFFHOOK','1001');s.run(2);add('duplicate_sample',len(s.calls)==1,s)
    s=connected();s.enqueue(1000,'ONHOOK','1001');s.enqueue(1100,'ONHOOK','1002');dial(s,'1001','1002',1200);s.enqueue(2000,'OFFHOOK','1002');s.run();add('reuse_after_release',s.calls['C2'].state=='CONNECTED' and len(s.tables.pairs)==1,s)
    return results,logs
