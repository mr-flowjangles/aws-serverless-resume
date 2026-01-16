"""
Lambda handler for FastAPI using Mangum.
This allows the entire FastAPI app to run in a single Lambda function.
"""
from mangum import Mangum
from main import app

# Mangum wraps the FastAPI app for Lambda
handler = Mangum(app)