import pytest
from unittest.mock import Mock, patch
import requests
from app.monitor import check_website_status
from app.models import Website, StatusCheck, DiscordWebhook
from datetime import datetime, timedelta, UTC

@pytest.fixture
def mock_db():
    db = Mock()
    # Configure the mock to return an empty list for webhooks query
    db.query.return_value.all.return_value = []
    # Configure the mock for previous status check query
    db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
    return db

@pytest.fixture
def sample_website():
    return Website(
        id=1,
        url="https://example.com",
        name="Test Site",
        check_interval_seconds=300,
        expected_status_code=200
    )

def test_successful_website_check(mock_db, sample_website):
    with patch('requests.get') as mock_get:
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_get.return_value = mock_response

        # Perform the check
        status_check = check_website_status(mock_db, sample_website)

        # Verify the results
        assert status_check.status == "up"
        assert status_check.error_message is None
        assert status_check.response_time_ms is not None
        assert mock_db.add.called
        assert mock_db.commit.called

def test_failed_website_check(mock_db, sample_website):
    with patch('requests.get') as mock_get:
        # Mock failed response with RequestException
        mock_get.side_effect = requests.RequestException("Connection failed")

        # Perform the check
        status_check = check_website_status(mock_db, sample_website)

        # Verify the results
        assert status_check.status == "down"
        assert "Connection failed" in status_check.error_message
        assert status_check.response_time_ms is None
        assert mock_db.add.called
        assert mock_db.commit.called

def test_wrong_status_code(mock_db, sample_website):
    with patch('requests.get') as mock_get:
        # Mock response with wrong status code
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.elapsed.total_seconds.return_value = 0.5
        mock_get.return_value = mock_response

        # Perform the check
        status_check = check_website_status(mock_db, sample_website)

        # Verify the results
        assert status_check.status == "down"
        assert "Unexpected status code: 404" in status_check.error_message
        assert mock_db.add.called
        assert mock_db.commit.called

def test_discord_notification(mock_db, sample_website):
    webhook = DiscordWebhook(id=1, url="https://discord.webhook.url", name="Test Webhook")
    
    # Configure mock_db to return our webhook
    mock_db.query.return_value.all.side_effect = None
    mock_db.query.return_value.all.return_value = [webhook]
    
    # Configure mock_db for previous status check
    previous_check = StatusCheck(
        website_id=1,
        status="up",
        checked_at=datetime.now(UTC) - timedelta(minutes=5)
    )
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = previous_check

    with patch('app.discord.send_discord_notification') as mock_send, \
         patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # Mock website check failure
        mock_get.side_effect = requests.RequestException("Test error")
        
        # Mock successful Discord webhook POST
        mock_post.return_value = Mock(status_code=204)
        
        # Perform the check
        status_check = check_website_status(mock_db, sample_website)

        # Verify Discord notification was attempted
        assert mock_post.called
        assert status_check.status == "down" 