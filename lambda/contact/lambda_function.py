"""
Lambda function for /contact endpoint
"""
import json
import os
import urllib.request
import urllib.parse

def lambda_handler(event, context):
    """
    Handle contact form submission with reCAPTCHA verification.
    
    Args:
        event: API Gateway event with body containing form data
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        name = body.get('name')
        email = body.get('email')
        message = body.get('message')
        recaptcha_token = body.get('recaptcha_token')
        
        # Validate required fields
        if not all([name, email, message, recaptcha_token]):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'detail': 'Missing required fields'})
            }
        
        # Verify reCAPTCHA
        recaptcha_secret = os.environ.get('RECAPTCHA_SECRET_KEY', '')
        if recaptcha_secret:
            is_valid = verify_recaptcha(recaptcha_token, recaptcha_secret)
            if not is_valid:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'detail': 'reCAPTCHA verification failed'})
                }
        
        # Log contact form submission (in production, send via SES)
        print("=" * 50)
        print("NEW CONTACT FORM SUBMISSION")
        print("=" * 50)
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Message: {message}")
        print("=" * 50)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'success',
                'message': "Thank you for your message! I'll get back to you soon."
            })
        }
        
    except Exception as e:
        print(f"Error processing contact form: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'detail': 'Failed to process contact form'})
        }


def verify_recaptcha(token, secret):
    """Verify reCAPTCHA token with Google."""
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
            result = json.loads(response.read().decode('utf-8'))
            return result.get('success', False)
    except Exception as e:
        print(f"reCAPTCHA verification error: {e}")
        return False
