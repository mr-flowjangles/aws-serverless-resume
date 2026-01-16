"""
FastAPI router for contact endpoint.
Uses handler logic from handlers.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from handlers import contact

router = APIRouter()


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str
    recaptcha_token: str


@router.post("/contact")
async def submit_contact(form: ContactForm):
    """Handle contact form submission with reCAPTCHA verification."""
    try:
        result = await contact.submit_contact_async(
            name=form.name,
            email=form.email,
            message=form.message,
            recaptcha_token=form.recaptcha_token
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to process contact form")
