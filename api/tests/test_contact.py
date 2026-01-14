"""
Test contact handler directly (tests both FastAPI and Lambda).
"""
import pytest
from handlers import contact
from unittest.mock import patch


def test_submit_contact_sync():
    """Test sync contact submission (for Lambda)."""
    print("\nTesting contact handler (sync)")
    
    # Mock reCAPTCHA verification
    with patch.object(contact, '_verify_recaptcha_sync', return_value=True):
        result = contact.submit_contact_sync(
            name="Test User",
            email="test@example.com",
            message="Test message",
            recaptcha_token="fake_token"
        )
    
    assert result["status"] == "success"
    assert "message" in result


def test_submit_contact_sync_invalid_recaptcha():
    """Test that invalid reCAPTCHA raises error."""
    # Mock reCAPTCHA verification to fail
    with patch.object(contact, '_verify_recaptcha_sync', return_value=False):
        with pytest.raises(ValueError, match="reCAPTCHA verification failed"):
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
    
    # Mock reCAPTCHA verification
    with patch.object(contact, '_verify_recaptcha_async', return_value=True):
        result = await contact.submit_contact_async(
            name="Test User",
            email="test@example.com",
            message="Test message",
            recaptcha_token="fake_token"
        )
    
    assert result["status"] == "success"
    assert "message" in result
