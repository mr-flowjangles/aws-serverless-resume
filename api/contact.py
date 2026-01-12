from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import httpx
import os
import logging

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# reCAPTCHA secret key - set this in your environment variables
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str
    recaptcha_token: str


async def verify_recaptcha(token: str) -> bool:
    """Verify reCAPTCHA token with Google."""
    if not RECAPTCHA_SECRET_KEY:
        logger.warning("RECAPTCHA_SECRET_KEY not set, skipping verification")
        return True
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": RECAPTCHA_SECRET_KEY,
                "response": token,
            },
        )
        result = response.json()
        return result.get("success", False)


@router.post("/contact")
async def submit_contact(form: ContactForm):
    """
    Handle contact form submission with reCAPTCHA verification.
    For now, logs to console. In production, would send via SES.
    """
    # Verify reCAPTCHA first
    is_valid = await verify_recaptcha(form.recaptcha_token)
    if not is_valid:
        logger.warning("reCAPTCHA verification failed")
        raise HTTPException(status_code=400, detail="reCAPTCHA verification failed")
    
    try:
        logger.info("=" * 50)
        logger.info("NEW CONTACT FORM SUBMISSION")
        logger.info("=" * 50)
        logger.info(f"Name: {form.name}")
        logger.info(f"Email: {form.email}")
        logger.info(f"Message: {form.message}")
        logger.info("=" * 50)
        
        return {
            "status": "success",
            "message": "Thank you for your message! I'll get back to you soon."
        }
    
    except Exception as e:
        logger.error(f"Error processing contact form: {e}")
        raise HTTPException(status_code=500, detail="Failed to process contact form")