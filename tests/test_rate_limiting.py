import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import patch, AsyncMock
from reply_sms import app, request_tracker, STATIC_WARNING

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        request_tracker.clear()
        yield client

# this patch is for external services so the test runs instantly and doesn't write to useronline.json
@patch('reply_sms.update_user_status')
@patch('reply_sms.Runner')
@patch('reply_sms.session_service')
def test_rate_limiter_blocks_after_10_requests(mock_session, mock_runner, mock_update, client):
    mock_session.get_session = AsyncMock(return_value=True)
    
    payload = {"From": "+19165550123", "Body": "Spam message"}
    # sends 10 spam messages
    for _ in range(10):
        response = client.post('/reply_sms', data=payload)
        assert STATIC_WARNING not in response.get_data(as_text=True)
        
    # 11th should be blocked and pass test
    response = client.post('/reply_sms', data=payload)
    assert STATIC_WARNING in response.get_data(as_text=True)