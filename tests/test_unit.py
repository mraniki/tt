"""
 TT test
"""

from unittest.mock import AsyncMock
import pytest

import iamlistening
from iamlistening import Listener
from fastapi.testclient import TestClient
from telethon import errors

from tt.utils import send_notification, start_listener, handle_messages
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


@pytest.mark.asyncio
async def test_send_notification(caplog):
    await send_notification("Test message")
    assert "json://localhost/" in caplog.text


@pytest.mark.asyncio
async def test_start_listener():
    # Mock the Listener and PluginManager objects
    listener_mock = AsyncMock()
    plugin_manager_mock = AsyncMock()

    # Set the run_forever and start_all_plugins methods
    listener_mock.run_forever.return_value = None
    plugin_manager_mock.start_all_plugins.return_value = None

    # Set the plugin_enabled setting to True
    settings.plugin_enabled = True

    # Call the start_listener function
    await start_listener()

    # Assert that the run_forever and start_all_plugins methods are called
    listener_mock.run_forever.assert_called_once()
    plugin_manager_mock.start_all_plugins.assert_called_once()

@pytest.mark.asyncio
async def test_handle_messages():
    # Mock the Listener and Plugin objects
    listener_mock = AsyncMock()
    plugin_mock = AsyncMock()

    # Set the get_latest_message and process_message methods for the mocks
    listener_mock.get_latest_message.return_value = "Test message"
    plugin_mock.process_message.return_value = None

    # Set the plugin_enabled setting to True
    settings.plugin_enabled = True

    # Call the handle_messages function
    await handle_messages(listener_mock, [plugin_mock])

    # Assert that the get_latest_message and process_message methods are called
    listener_mock.get_latest_message.assert_called_once()
    plugin_mock.process_message.assert_called_once_with("Test message")