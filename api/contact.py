from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import logging

router = APIRouter()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    message: str

@router.post("/contact")
async def submit_contact(form: ContactForm):
    """
    Handle contact form submission
    For now, logs to console. In production, would send via SES.
    """
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