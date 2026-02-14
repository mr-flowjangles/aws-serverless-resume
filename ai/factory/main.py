"""
Bot Factory — Standalone Server

Run this to use the bot factory without the resume site.

Usage:
    uvicorn factory.main:app --reload --port 8080

Or from within a parent project:
    uvicorn ai.factory.main:app --reload --port 8080
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# When running standalone, import from this package
from . import factory_router

app = FastAPI(title="Bot Factory")

# CORS — adjust origins for your deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all enabled bots
app.include_router(factory_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "bot-factory"}
