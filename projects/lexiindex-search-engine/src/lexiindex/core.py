"""Transactional SQLite FTS-free inverted index with deterministic BM25 scoring."""
import math
import re
import sqlite3
from collections import Counter
from pathlib import Path

TOKEN = re.compile(r"[a-z0-9]+")

def tokenize(text):
    if not isinstance(text, str):
        raise TypeError('text must be a string')
    return TOKEN.findall(text.casefold())

class Index:
    def __init__(self, path=':memory:'):
        self.db = sqlite3.connect(str(path))
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL, length INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS postings(term TEXT NOT NULL, doc_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE, tf INTEGER NOT NULL, positions TEXT NOT NULL, PRIMARY KEY(term,doc_id));
        CREATE INDEX IF NOT EXISTS postings_doc ON postings(doc_id);
        ''')
    def close(self): self.db.close()
    def upsert(self, doc_id, title, body):
        if not all(isinstance(x,str) for x in (doc_id,title,body)) or not doc_id.strip():
            raise ValueError('id, title and body must be strings; id nonempty')
        tokens=tokenize(title+' '+body)
        positions={}
        for pos,word in enumerate(tokens): positions.setdefault(word,[]).append(pos)
        with self.db:
            self.db.execute('DELETE FROM documents WHERE id=?',(doc_id,))
            self.db.execute('INSERT INTO documents VALUES (?,?,?,?)',(doc_id,title,body,len(tokens)))
            self.db.executemany('INSERT INTO postings VALUES (?,?,?,?)',[(term,doc_id,len(pos),','.join(map(str,pos))) for term,pos in positions.items()])
    def delete(self, doc_id):
        with self.db:
            return self.db.execute('DELETE FROM documents WHERE id=?',(doc_id,)).rowcount
    def stats(self):
        n,total=self.db.execute('SELECT COUNT(*),COALESCE(SUM(length),0) FROM documents').fetchone()
        return {'documents':n,'tokens':total,'average_length':total/n if n else 0}
    def search(self, query, limit=10, phrase=False, k1=1.2, b=.75):
        if type(limit) is not int or limit<1 or limit>1000: raise ValueError('limit must be 1..1000')
        if not (k1>0 and 0<=b<=1): raise ValueError('invalid BM25 parameters')
        terms=tokenize(query)
        if not terms:return []
        n,total=self.db.execute('SELECT COUNT(*),COALESCE(SUM(length),0) FROM documents').fetchone()
        if not n:return []
        avg=total/n
        scores={}; match={}
        for term in sorted(set(terms)):
            rows=self.db.execute('SELECT p.doc_id,p.tf,p.positions,d.length FROM postings p JOIN documents d ON d.id=p.doc_id WHERE p.term=?',(term,)).fetchall()
            df=len(rows)
            if not df:continue
            idf=math.log(1+(n-df+.5)/(df+.5))
            for doc,tf,positions,length in rows:
                scores[doc]=scores.get(doc,0)+idf*(tf*(k1+1))/(tf+k1*(1-b+b*length/avg))
                match.setdefault(doc,{})[term]=set(map(int,positions.split(',')))
        if phrase:
            scores={doc:score for doc,score in scores.items() if all(term in match[doc] for term in terms) and any(all(start+i in match[doc][term] for i,term in enumerate(terms)) for start in match[doc][terms[0]])}
        results=[]
        for doc,score in sorted(scores.items(),key=lambda kv:(-kv[1],kv[0]))[:limit]:
            title,body=self.db.execute('SELECT title,body FROM documents WHERE id=?',(doc,)).fetchone()
            results.append({'id':doc,'title':title,'score':round(score,8),'snippet':body[:160]})
        return results
