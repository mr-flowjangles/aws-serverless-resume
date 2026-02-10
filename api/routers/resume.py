"""
FastAPI router for resume endpoint.

Single endpoint returns all resume data in one payload.
Data is cached at the handler level — see handlers/resume_all.py.
"""
from fastapi import APIRouter, HTTPException
from handlers.resume_all import get_all_resume_data

router = APIRouter()


@router.get("/resume")
def get_resume():
    """
    Return complete resume data: profile, work experience, education, skills.
    
    Single DynamoDB scan on first call, cached for subsequent requests.
    """
    try:
        return get_all_resume_data()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading resume data: {str(e)}"
        )
