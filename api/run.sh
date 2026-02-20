#!/bin/bash
exec python -m uvicorn main:app --host 0.0.0.0 --port 8080