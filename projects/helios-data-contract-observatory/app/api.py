from fastapi import FastAPI
app=FastAPI(title='Helios Data Contract Observatory')
@app.get('/health')
def health():
    return {'status':'ok'}
