Here's a test for the changes in the given git output:

```python
import pytest
from fastapi.testclient import TestClient
from your_app import app, logger
from unittest.mock import MagicMock

client = TestClient(app)

def test_start_bot_error_handling(monkeypatch):
    async def mock_listener():
        raise Exception("Test exception")

    monkeypatch.setattr("your_app.listener", mock_listener)
    logger.error = MagicMock()

    with pytest.raises(Exception):
        await app.start_bot()

    logger.error.assert_called_once_with("Test exception")

def test_webhook(monkeypatch):
    async def mock_send_notification(data):
        pass

    monkeypatch.setattr("your_app.send_notification", mock_send_notification)
    monkeypatch.setattr("your_app.settings.webhook_secret", "test_secret")

    response = client.post("/webhook", json={"key": "test_secret"})
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

    response = client.post("/webhook", json={"key": "wrong_secret"})
    assert response.status_code == 200
    assert response.json() == {"status": "ERROR"}
```

Replace `your_app` with the actual name of your app's module. This test checks the error handling in the `start_bot` function and the `/webhook` endpoint.