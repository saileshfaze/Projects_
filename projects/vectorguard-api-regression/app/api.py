from fastapi import FastAPI
app=FastAPI(title='VectorGuard Semantic API Regression')
@app.get('/health')
def health():
    return {'status':'ok'}
