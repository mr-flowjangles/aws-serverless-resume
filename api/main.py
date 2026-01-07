from fastapi import FastAPI
from chat import router as chat_router
from health import router as health_router
from resume import router as resume_router

app = FastAPI(servers=[{"url": "/api"}])
app.include_router(chat_router)
app.include_router(health_router)
app.include_router(resume_router)

@app.get("/hello")
def hello():
    return {"message": "hello from fastAPI, sup dog"}