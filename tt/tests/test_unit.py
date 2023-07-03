"""
 TT test
"""
import pytest
import iamlistening
from iamlistening import Listener
from fastapi.testclient import TestClient
from tt.utils import send_notification
from tt.bot import app
from tt.config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="order")
def order_params():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'WBTC',
        'quantity': 1,
    }


@pytest.fixture(name="wrong_order")
def wrong_order():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'NOTATHING',
        'quantity': 1,
    }


@pytest.mark.asyncio
async def test_listener_telegram():
    listener_test = Listener()
    print(listener_test)
    assert listener_test is not None
    assert isinstance(listener_test, iamlistening.main.Listener)
    await listener_test.handle_message("hello")
    msg = await listener_test.get_latest_message()
    print(msg)
    assert msg == "hello"


def test_read_main():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200


def test_read_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_webhook_with_valid_auth():
    client = TestClient(app)
    payload = {"data": "buy BTC"}
    response = client.post("/webhook/123abc", json=payload)
    print(response)
    assert response is not None
    assert response.content.decode('utf-8') == '{"status":"OK"}'


def test_webhook_with_invalid_auth():
    client = TestClient(app)
    payload = {"data": "my_data"}
    print(payload)
    response = client.post("/webhook/abc123", json=payload)
    assert response.content.decode('utf-8') == '{"detail":"Not Found"}'


@pytest.mark.asyncio
async def test_send_notification(caplog):
    await send_notification("Test message")
    assert "json://localhost/" in caplog.text
