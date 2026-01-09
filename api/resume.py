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

def _get_dynamodb_table():
    """Helper function to get DynamoDB table connection"""
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
        region_name=os.getenv('AWS_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    return dynamodb.Table('ResumeData')

@router.get("/resume/work-experience")
def get_work_experience():
    """Get work experience items sorted by date (most recent first)"""
    table = _get_dynamodb_table()
    
    response = table.query(
        IndexName='TypeIndex',
        KeyConditionExpression='#t = :type',
        ExpressionAttributeNames={'#t': 'type'},
        ExpressionAttributeValues={':type': 'work_experience'}
    )
    
    items = response.get('Items', [])
    
    # Sort: current jobs first, then by start date descending
    items.sort(key=lambda x: (
        x.get('is_current', False),  # True sorts after False, so negate in next line
        x.get('start_date', '')
    ), reverse=True)
    
    return {"items": items}

@router.get("/resume/education")
def get_education():
    """Get education items sorted by date (most recent first)"""
    table = _get_dynamodb_table()
    
    response = table.query(
        IndexName='TypeIndex',
        KeyConditionExpression='#t = :type',
        ExpressionAttributeNames={'#t': 'type'},
        ExpressionAttributeValues={':type': 'education'}
    )
    
    items = response.get('Items', [])
    
    # Sort by start date descending
    items.sort(key=lambda x: x.get('start_date', ''), reverse=True)
    
    return {"items": items}

@router.get("/resume/skills")
def get_skills():
    """Get skills organized by category"""
    table = _get_dynamodb_table()
    
    response = table.query(
        IndexName='TypeIndex',
        KeyConditionExpression='#t = :type',
        ExpressionAttributeNames={'#t': 'type'},
        ExpressionAttributeValues={':type': 'skills'}
    )
    
    items = response.get('Items', [])
    
    # Sort by sort_order if present, otherwise by category name
    items.sort(key=lambda x: (
        x.get('sort_order', 999),
        x.get('category', '')
    ))
    
    return {"items": items}