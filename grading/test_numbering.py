from src.numbering import analyze_number as f
P=['1001','1002','1003','1004']
def test_prefix():assert all(f(x,P,'1001')=='INCOMPLETE' for x in ['', '1','10','100'])
def test_local():assert f('1002',P,'1001')=='LOCAL'
def test_self():assert f('1001',P,'1001')=='SELF_CALL'
def test_invalid():assert all(f(x,P,'1001')=='INVALID' for x in ['9','1009','10022','a'])
def test_configured():assert f('2002',['2001','2002'],'2001')=='LOCAL'
