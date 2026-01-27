"""
Shared contact form handler logic.
"""
import os
import boto3
from botocore.exceptions import ClientError

try:
    import httpx  # For FastAPI async
    HTTPX_AVAILABLE = True
except ImportError:
    import urllib.request
    import urllib.parse
    HTTPX_AVAILABLE = False


# Initialize SES client
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_ENDPOINT_URL = os.getenv('AWS_ENDPOINT_URL')  # For LocalStack

# Create SES client with LocalStack support
if AWS_ENDPOINT_URL:
    # Local development with LocalStack
    ses_client = boto3.client(
        'ses',
        region_name=AWS_REGION,
        endpoint_url=AWS_ENDPOINT_URL,
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
    )
else:
    # Production - use real AWS
    ses_client = boto3.client('ses', region_name=AWS_REGION)


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
        Exception: If email sending fails
    """
    recaptcha_secret = os.getenv('RECAPTCHA_SECRET_KEY', '')
    
    if recaptcha_secret:
        is_valid = await _verify_recaptcha_async(recaptcha_token, recaptcha_secret)
        if not is_valid:
            raise ValueError('reCAPTCHA verification failed')
    
    # Send email via SES
    await _send_email_async(name, email, message)
    
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
        Exception: If email sending fails
    """
    recaptcha_secret = os.getenv('RECAPTCHA_SECRET_KEY', '')
    
    if recaptcha_secret:
        is_valid = _verify_recaptcha_sync(recaptcha_token, recaptcha_secret)
        if not is_valid:
            raise ValueError('reCAPTCHA verification failed')
    
    # Send email via SES
    _send_email_sync(name, email, message)
    
    return {
        'status': 'success',
        'message': "Thank you for your message! I'll get back to you soon."
    }


async def _send_email_async(name, sender_email, message):
    """Send email via AWS SES (async)."""
    from_email = os.getenv('SES_FROM_EMAIL', 'robmrose@me.com')
    to_email = os.getenv('SES_TO_EMAIL', 'robmrose@me.com')
    
    subject = f"Contact Form: Message from {name}"
    body_text = f"""
New contact form submission from robrose.info

Name: {name}
Email: {sender_email}

Message:
{message}

---
Sent from robrose.info contact form
"""
    
    body_html = f"""
<html>
<head></head>
<body>
  <h2>New contact form submission from robrose.info</h2>
  <p><strong>Name:</strong> {name}</p>
  <p><strong>Email:</strong> {sender_email}</p>
  <p><strong>Message:</strong></p>
  <p>{message.replace(chr(10), '<br>')}</p>
  <hr>
  <p style="color: #666; font-size: 12px;">Sent from robrose.info contact form</p>
</body>
</html>
"""
    
    try:
        response = ses_client.send_email(
            Source=from_email,
            Destination={
                'ToAddresses': [to_email]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': body_html,
                        'Charset': 'UTF-8'
                    }
                }
            },
            ReplyToAddresses=[sender_email]
        )
        print(f"Email sent successfully. Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Error sending email: {e.response['Error']['Message']}")
        raise Exception("Failed to send email")


def _send_email_sync(name, sender_email, message):
    """Send email via AWS SES (sync)."""
    from_email = os.getenv('SES_FROM_EMAIL', 'robmrose@me.com')
    to_email = os.getenv('SES_TO_EMAIL', 'robmrose@me.com')
    
    subject = f"Contact Form: Message from {name}"
    body_text = f"""
New contact form submission from robrose.info

Name: {name}
Email: {sender_email}

Message:
{message}

---
Sent from robrose.info contact form
"""
    
    body_html = f"""
<html>
<head></head>
<body>
  <h2>New contact form submission from robrose.info</h2>
  <p><strong>Name:</strong> {name}</p>
  <p><strong>Email:</strong> {sender_email}</p>
  <p><strong>Message:</strong></p>
  <p>{message.replace(chr(10), '<br>')}</p>
  <hr>
  <p style="color: #666; font-size: 12px;">Sent from robrose.info contact form</p>
</body>
</html>
"""
    
    try:
        response = ses_client.send_email(
            Source=from_email,
            Destination={
                'ToAddresses': [to_email]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body_text,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': body_html,
                        'Charset': 'UTF-8'
                    }
                }
            },
            ReplyToAddresses=[sender_email]
        )
        print(f"Email sent successfully. Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Error sending email: {e.response['Error']['Message']}")
        raise Exception("Failed to send email")


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
