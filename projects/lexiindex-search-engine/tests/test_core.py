import pytest
from lexiindex import Index, tokenize

def test_tokens(): assert tokenize('HELLO, café! 123')==['hello','caf','123']
def test_empty():
    i=Index();assert i.search('anything')==[];assert i.stats()['documents']==0;i.close()
def test_bm25_ranking():
    i=Index();i.upsert('a','a','python python python');i.upsert('b','b','python');assert i.search('python')[0]['id']=='a';i.close()
def test_phrase():
    i=Index();i.upsert('a','title','red blue green');i.upsert('b','title','red green blue');assert [x['id'] for x in i.search('red blue',phrase=True)]==['a'];i.close()
def test_phrase_repeated():
    i=Index();i.upsert('a','','red red blue');assert i.search('red red',phrase=True);assert not i.search('red red red',phrase=True);i.close()
def test_upsert():
    i=Index();i.upsert('a','','old');i.upsert('a','','new');assert not i.search('old');assert i.search('new');assert i.stats()['documents']==1;i.close()
def test_delete():
    i=Index();i.upsert('a','','test');assert i.delete('a')==1;assert i.delete('a')==0;assert not i.search('test');i.close()
def test_tie_break():
    i=Index();i.upsert('z','','hello');i.upsert('a','','hello');assert [x['id'] for x in i.search('hello')]==['a','z'];i.close()
def test_persistence(tmp_path):
    path=tmp_path/'index.db';i=Index(path);i.upsert('x','x','hello');i.close();j=Index(path);assert j.search('hello')[0]['id']=='x';j.close()
def test_empty_query():
    i=Index();i.upsert('a','','hello');assert i.search('!!')==[];i.close()
@pytest.mark.parametrize('bad', ['',None,123])
def test_invalid_id(bad):
    i=Index()
    with pytest.raises(ValueError):i.upsert(bad,'title','body')
    i.close()
@pytest.mark.parametrize('limit',[0,-1,1001,1.5,True])
def test_invalid_limit(limit):
    i=Index()
    with pytest.raises(ValueError):i.search('x',limit=limit)
    i.close()
@pytest.mark.parametrize('b',[-.1,1.1])
def test_invalid_b(b):
    i=Index()
    with pytest.raises(ValueError):i.search('x',b=b)
    i.close()
def test_unicode_restriction():assert tokenize('naïve')==['na','ve']
def test_multi_term():
    i=Index();i.upsert('a','','alpha beta');i.upsert('b','','alpha');assert i.search('alpha beta')[0]['id']=='a';i.close()
