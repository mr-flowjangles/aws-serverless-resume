"""
Shared contact form handler logic.
"""
import os
try:
    import httpx  # For FastAPI async
    HTTPX_AVAILABLE = True
except ImportError:
    import urllib.request
    import urllib.parse
    HTTPX_AVAILABLE = False


async def submit_contact_async(name, email, message, recaptcha_token):
    """
    Handle contact form submission (async version for FastAPI).
    
    Args:
        name: Sender name
        email: Sender email
        message: Message content
        recaptcha_token: reCAPTCHA token
        
    Returns:
        dict: Response message
        
    Raises:
        ValueError: If reCAPTCHA verification fails
    """
    recaptcha_secret = os.getenv('RECAPTCHA_SECRET_KEY', '')
    
    if recaptcha_secret:
        is_valid = await _verify_recaptcha_async(recaptcha_token, recaptcha_secret)
        if not is_valid:
            raise ValueError('reCAPTCHA verification failed')
    
    # Log contact form (in production, send via SES)
    print("=" * 50)
    print("NEW CONTACT FORM SUBMISSION")
    print("=" * 50)
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Message: {message}")
    print("=" * 50)
    
    return {
        'status': 'success',
        'message': "Thank you for your message! I'll get back to you soon."
    }


def submit_contact_sync(name, email, message, recaptcha_token):
    """
    Handle contact form submission (sync version for Lambda).
    
    Args:
        name: Sender name
        email: Sender email
        message: Message content
        recaptcha_token: reCAPTCHA token
        
    Returns:
        dict: Response message
        
    Raises:
        ValueError: If reCAPTCHA verification fails
    """
    recaptcha_secret = os.getenv('RECAPTCHA_SECRET_KEY', '')
    
    if recaptcha_secret:
        is_valid = _verify_recaptcha_sync(recaptcha_token, recaptcha_secret)
        if not is_valid:
            raise ValueError('reCAPTCHA verification failed')
    
    # Log contact form (in production, send via SES)
    print("=" * 50)
    print("NEW CONTACT FORM SUBMISSION")
    print("=" * 50)
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Message: {message}")
    print("=" * 50)
    
    return {
        'status': 'success',
        'message': "Thank you for your message! I'll get back to you soon."
    }


async def _verify_recaptcha_async(token, secret):
    """Verify reCAPTCHA token (async)."""
    if not HTTPX_AVAILABLE:
        return True
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": secret, "response": token}
        )
        result = response.json()
        return result.get("success", False)


def _verify_recaptcha_sync(token, secret):
    """Verify reCAPTCHA token (sync)."""
    try:
        data = urllib.parse.urlencode({
            'secret': secret,
            'response': token
        }).encode('utf-8')
        
        req = urllib.request.Request(
            'https://www.google.com/recaptcha/api/siteverify',
            data=data,
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            import json
            result = json.loads(response.read().decode('utf-8'))
            return result.get('success', False)
    except Exception as e:
        print(f"reCAPTCHA verification error: {e}")
        return False
