"""
 TT test
"""

from unittest.mock import AsyncMock
import pytest
import asyncio

from iamlistening import Listener
from fastapi.testclient import TestClient

from tt.config import settings
from tt.bot import app
from tt.utils import send_notification, start_bot, start_listener, start_plugins, run_bot
from tt.plugins.plugin_manager import PluginManager



@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


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
    listener, task = await start_listener(max_iterations=1)
    assert isinstance(listener, Listener)
    assert isinstance(task, asyncio.Task)


@pytest.mark.asyncio
async def test_start_plugins():
    plugin_manager = AsyncMock(spec=PluginManager)
    await start_plugins(plugin_manager)
    plugin_manager.load_plugins.assert_called_once()


@pytest.mark.asyncio
async def test_start_bot():
    listener = AsyncMock(spec=Listener)
    plugin_manager = AsyncMock(spec=PluginManager)
    listener.get_latest_message.return_value = "Test message"

    await start_bot(listener, plugin_manager)

    listener.get_latest_message.assert_called_once()
    plugin_manager.process_message.assert_called_once_with("Test message")

@pytest.mark.asyncio
async def test_run_bot():
    mock_bot = AsyncMock()
    start_listener = AsyncMock()
    bot_task = asyncio.create_task(run_bot(bot=mock_bot))
    start_listener.assert_awaited_once()
    await bot_task