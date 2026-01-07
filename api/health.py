import boto3
import os
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/health")
def health_check():
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    try:
        # Check DynamoDB
        dynamodb = boto3.client(
            'dynamodb',
            endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        dynamodb.list_tables()
        health_status["services"]["dynamodb"] = "ok"
    except Exception as e:
        health_status["services"]["dynamodb"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    try:
        # Check S3
        s3 = boto3.client(
            's3',
            endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        s3.list_buckets()
        health_status["services"]["s3"] = "ok"
    except Exception as e:
        health_status["services"]["s3"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status