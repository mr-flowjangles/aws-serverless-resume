"""
Tests for contact handler.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from handlers import contact


def test_submit_contact_sync():
    """Test sync contact submission (for Lambda)."""
    print("\nTesting contact handler (sync)")

    # Mock both reCAPTCHA verification and SES client
    with patch.object(contact, '_verify_recaptcha_sync', return_value=True), \
         patch.object(contact, 'ses_client') as mock_ses:
        
        # Mock SES send_email response
        mock_ses.send_email.return_value = {'MessageId': 'test-message-id'}
        
        result = contact.submit_contact_sync(
            name="Test User",
            email="test@example.com",
            message="Test message",
            recaptcha_token="fake_token"
        )

        assert result['status'] == 'success'
        assert 'thank you' in result['message'].lower()
        
        # Verify SES was called with correct parameters
        mock_ses.send_email.assert_called_once()
        call_args = mock_ses.send_email.call_args[1]
        assert call_args['Source'] == 'robmrose@me.com'
        assert 'robmrose@me.com' in call_args['Destination']['ToAddresses']
        assert 'test@example.com' in call_args['ReplyToAddresses']


@patch.dict(os.environ, {'RECAPTCHA_SECRET_KEY': 'test_secret'})
def test_submit_contact_sync_invalid_recaptcha():
    """Test sync contact with invalid reCAPTCHA."""
    with patch.object(contact, '_verify_recaptcha_sync', return_value=False):
        with pytest.raises(ValueError, match='reCAPTCHA verification failed'):
            contact.submit_contact_sync(
                name="Test User",
                email="test@example.com",
                message="Test message",
                recaptcha_token="invalid_token"
            )


@pytest.mark.asyncio
async def test_submit_contact_async():
    """Test async contact submission (for FastAPI)."""
    print("\nTesting contact handler (async)")

    # Mock both reCAPTCHA verification and SES client
    with patch.object(contact, '_verify_recaptcha_async', return_value=True), \
         patch.object(contact, 'ses_client') as mock_ses:
        
        # Mock SES send_email response
        mock_ses.send_email.return_value = {'MessageId': 'test-message-id'}
        
        result = await contact.submit_contact_async(
            name="Test User",
            email="test@example.com",
            message="Test message",
            recaptcha_token="fake_token"
        )

        assert result['status'] == 'success'
        assert 'thank you' in result['message'].lower()
        
        # Verify SES was called with correct parameters
        mock_ses.send_email.assert_called_once()
        call_args = mock_ses.send_email.call_args[1]
        assert call_args['Source'] == 'robmrose@me.com'
        assert 'robmrose@me.com' in call_args['Destination']['ToAddresses']
        assert 'test@example.com' in call_args['ReplyToAddresses']


@patch.dict(os.environ, {'RECAPTCHA_SECRET_KEY': 'test_secret'})
@pytest.mark.asyncio
async def test_submit_contact_async_invalid_recaptcha():
    """Test async contact with invalid reCAPTCHA."""
    with patch.object(contact, '_verify_recaptcha_async', return_value=False):
        with pytest.raises(ValueError, match='reCAPTCHA verification failed'):
            await contact.submit_contact_async(
                name="Test User",
                email="test@example.com",
                message="Test message",
                recaptcha_token="invalid_token"
            )


@pytest.mark.asyncio
async def test_submit_contact_async_ses_failure():
    """Test async contact with SES failure."""
    from botocore.exceptions import ClientError
    
    with patch.object(contact, '_verify_recaptcha_async', return_value=True), \
         patch.object(contact, 'ses_client') as mock_ses:
        
        # Mock SES failure
        error_response = {'Error': {'Code': 'MessageRejected', 'Message': 'Email rejected'}}
        mock_ses.send_email.side_effect = ClientError(error_response, 'SendEmail')
        
        with pytest.raises(Exception, match='Failed to send email'):
            await contact.submit_contact_async(
                name="Test User",
                email="test@example.com",
                message="Test message",
                recaptcha_token="fake_token"
            )


def test_submit_contact_sync_ses_failure():
    """Test sync contact with SES failure."""
    from botocore.exceptions import ClientError
    
    with patch.object(contact, '_verify_recaptcha_sync', return_value=True), \
         patch.object(contact, 'ses_client') as mock_ses:
        
        # Mock SES failure
        error_response = {'Error': {'Code': 'MessageRejected', 'Message': 'Email rejected'}}
        mock_ses.send_email.side_effect = ClientError(error_response, 'SendEmail')
        
        with pytest.raises(Exception, match='Failed to send email'):
            contact.submit_contact_sync(
                name="Test User",
                email="test@example.com",
                message="Test message",
                recaptcha_token="fake_token"
            )
