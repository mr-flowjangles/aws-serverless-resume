from fastapi import FastAPI
from chat import router as chat_router
from health import router as health_router

app = FastAPI(servers=[{"url": "/api"}])
app.include_router(chat_router)
app.include_router(health_router)

@app.get("/hello")
def hello():
    return {"message": "hello from fastAPI, sup dog"}