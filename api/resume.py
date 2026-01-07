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

# Placeholder endpoints for DynamoDB data (we'll build these next)
@router.get("/resume")
def list_resume_items():
    """List resume items by type"""
    return {"items": []}