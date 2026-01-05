from fastapi import FastAPI
from chat import router as chat_router

app = FastAPI(servers=[{"url": "/api"}])
app.include_router(chat_router)

@app.get("/hello")
def hello():
    return {"message": "hello from fastAPI, sup dog"}