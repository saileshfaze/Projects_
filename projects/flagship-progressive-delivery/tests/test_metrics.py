from flagship.metrics import summarize

def test_empty():assert summarize([])==[]
def test_counts():
    result=summarize([{'subject':'a','variation':'x','converted':True},{'subject':'b','variation':'x','converted':False}])[0]
    assert result.exposures==2 and result.conversions==1 and result.rate==.5

def test_dedup():
    result=summarize([{'subject':'a','variation':'x','converted':False},{'subject':'a','variation':'x','converted':True}])[0]
    assert result.exposures==1 and result.conversions==1

def test_bounds():
    result=summarize([{'subject':str(i),'variation':'x','converted':i%2==0} for i in range(100)])[0]
    assert 0<=result.wilson_low<=result.rate<=result.wilson_high<=1
