"""
FastAPI router for resume endpoints.
Uses shared handler logic from shared.handlers.
"""
from fastapi import APIRouter, HTTPException
from shared.handlers import profile, work_experience, education, skills

router = APIRouter()


@router.get("/resume/profile")
def get_profile():
    """Get profile from DynamoDB."""
    try:
        return profile.get_profile()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading profile: {str(e)}")


@router.get("/resume/work-experience")
def get_work_experience():
    """Get work experience items sorted by date (most recent first)."""
    try:
        items = work_experience.get_work_experience()
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading work experience: {str(e)}")


@router.get("/resume/education")
def get_education():
    """Get education items sorted by date (most recent first)."""
    try:
        items = education.get_education()
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading education: {str(e)}")


@router.get("/resume/skills")
def get_skills():
    """Get skills organized by category."""
    try:
        items = skills.get_skills()
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading skills: {str(e)}")
