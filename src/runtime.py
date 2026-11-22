"""教师框架：串行事件、逻辑时钟、资源预留和真实T/S接口。"""
from dataclasses import dataclass,field
import heapq,itertools
from src.switch_models import Tables,Endpoint
from src.switch_connections import connect_pair,disconnect_pair
from src.hooks import detect_hook_events
from src.control import handle_call_event
from src.timeouts import handle_timeout

@dataclass
class Call:
    call_id:str
    caller:str
    callee:str|None=None
    state:str='COLLECTING'
    digits:str=''
    timer:int=0
    timer_kind:str|None=None
    reason:str=''

class Exchange:
    def __init__(self):
        self.numbers=['1001','1002','1003','1004'];self.hooks=dict.fromkeys(self.numbers,0)
        self.owners={};self.waiting=set();self.calls={};self.tables=Tables()
        self.now=0;self.queue=[];self.sequence=itertools.count();self.serial=0;self.logs=[]
        self.endpoints={n:Endpoint(0,i+1) for i,n in enumerate(self.numbers)}
    def enqueue(self,time,kind,user=None,value=None,call_id=None,token=None):
        if time<self.now:raise ValueError('事件不能早于当前逻辑时间')
        heapq.heappush(self.queue,(time,next(self.sequence),{'kind':kind,'user':user,'value':value,'call_id':call_id,'token':token}))
    def arm(self,c,kind,delay):
        c.timer+=1;c.timer_kind=kind
        self.enqueue(self.now+delay,'TIMEOUT',value=kind,call_id=c.call_id,token=c.timer)
    def cancel(self,c):c.timer+=1;c.timer_kind=None
    def reserve(self,c,n):
        if self.hooks[n] or n in self.owners or n in self.waiting:return False
        c.callee=n;self.owners[n]=c.call_id;return True
    def activate(self,c):return connect_pair(c.call_id,self.endpoints[c.caller],self.endpoints[c.callee],self.tables)
    def finish(self,c,reason):
        disconnect_pair(c.call_id,self.tables);self.cancel(c);c.state='ENDED';c.reason=reason
        for n in [c.caller,c.callee]:
            if n is not None and self.owners.get(n)==c.call_id:
                del self.owners[n]
                if self.hooks[n]:self.waiting.add(n)
    def action(self,actions,name,**kw):actions.append({'type':name,**kw})
    def dispatch(self,e):
        actions=[];c=None;before='IDLE'
        if e['kind'] in ['OFFHOOK','ONHOOK']:
            n=e['user'];previous=self.hooks.copy();current=self.hooks.copy();current[n]=int(e['kind']=='OFFHOOK')
            events=detect_hook_events(previous,current);self.hooks=current
            if not events:return
        n=e.get('user')
        if n in self.waiting:
            if e['kind']=='ONHOOK':self.waiting.remove(n)
            self.logs.append({'time_ms':self.now,'event':e,'call_id':None,'before':'WAIT_ONHOOK','after':'IDLE' if n not in self.waiting else 'WAIT_ONHOOK','actions':[],'reason':''});return
        if e['kind']=='TIMEOUT':c=self.calls.get(e['call_id'])
        elif n in self.owners:c=self.calls[self.owners[n]]
        elif e['kind']=='OFFHOOK':
            self.serial+=1;c=Call(f'C{self.serial}',n);self.calls[c.call_id]=c;self.owners[n]=c.call_id
        if c:
            before=c.state
            if e['kind']=='TIMEOUT':handle_timeout(c,e,self,actions)
            else:handle_call_event(c,e,self,actions)
        self.logs.append({'time_ms':self.now,'event':e,'call_id':c.call_id if c else None,'before':before,'after':c.state if c else 'IDLE','actions':actions,'reason':c.reason if c else ''})
    def run(self,until=None):
        while self.queue and (until is None or self.queue[0][0]<=until):
            self.now,_,e=heapq.heappop(self.queue);self.dispatch(e)
        return self
