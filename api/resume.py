import boto3
import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

router = APIRouter()

# Path to config file
CONFIG_PATH = Path("/app/config/general-data.json")

def load_config():
    """Load general data from config file"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Config file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid config file")

@router.get("/resume/profile")
def get_profile():
    """Get profile from config file"""
    config = load_config()
    return config['profile']

@router.get("/resume")
def list_resume_items(type: str = None):
    """List resume items by type (experience, skills, education, projects)"""
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    table = dynamodb.Table('ResumeData')
    
    if type:
        # Query by type using GSI
        response = table.query(
            IndexName='TypeIndex',
            KeyConditionExpression='#t = :type',
            ExpressionAttributeNames={'#t': 'type'},
            ExpressionAttributeValues={':type': type}
        )
    else:
        # Scan all items
        response = table.scan()
    
    items = response.get('Items', [])
    
    # Sort experience by date (most recent first)
    if type == 'experience':
        items.sort(key=lambda x: (
            x.get('endDate') == 'present',  # Present jobs first
            x.get('startDate', '')
        ), reverse=True)
    
    return {"items": items}