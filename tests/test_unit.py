"""
 TT test
"""

from unittest.mock import AsyncMock
import pytest

import iamlistening
from iamlistening import Listener
from fastapi.testclient import TestClient
from telethon import errors

from tt.utils import send_notification, listener
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


@pytest.fixture(name="listener_obj")
def listener_test():
    return Listener()

@pytest.fixture
def message():
    return "Test message"


@pytest.mark.asyncio
async def test_send_notification(caplog):
    await send_notification("Test message")
    assert "json://localhost/" in caplog.text


@pytest.mark.asyncio
async def test_listener_telegram(listener_obj):
    print(listener_obj)
    assert listener_obj is not None
    assert isinstance(listener_obj, iamlistening.main.Listener)
    await listener_obj.handle_message("hello")
    msg = await listener_obj.get_latest_message()
    print(msg)
    assert msg == "hello"

@pytest.mark.asyncio
async def test_get_latest_message(listener_obj, message):
    await listener_obj.handle_message(message)
    assert await listener_obj.get_latest_message() == message


@pytest.mark.asyncio
async def test_listener_run_error(listener_obj):
    with pytest.raises(errors.ApiIdInvalidError):
        start = AsyncMock()
        await listener_obj.run_forever(max_iterations=1)
        assert start.assert_awaited_once()


@pytest.mark.asyncio
async def test_listener():
    await listener()
    assert Listener.assert_called_once() 


def test_app_endpoint_main():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200


def test_app_health():
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
