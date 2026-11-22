import pytest
from src.hooks import detect_hook_events as f

def test_offhook():assert f({'1001':0},{'1001':1})==[{'user':'1001','kind':'OFFHOOK'}]
def test_onhook():assert f({'1001':1},{'1001':0})==[{'user':'1001','kind':'ONHOOK'}]
def test_unchanged():assert f({'1001':1},{'1001':1})==[]
def test_sorted_and_pure():
    a={'1002':0,'1001':1};b={'1002':1,'1001':0}
    assert [x['user'] for x in f(a,b)]==['1001','1002'] and a['1001']==1
def test_bad_values():
    with pytest.raises(ValueError):f({'1001':0},{'1001':2})
def test_bad_users():
    with pytest.raises(ValueError):f({'1001':0},{'1002':0})
