"""
 TT test
"""
import asyncio
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from iamlistening import Listener

from tt.bot import app
from tt.config import settings
from tt.plugins.plugin_manager import BasePlugin, PluginManager
from tt.utils import run_bot, send_notification, start_bot, start_plugins


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="message")
def message_test():
    return "Test message"

@pytest.fixture(name="listener_obj")
def listener_test():
    return Listener()

@pytest.fixture(name="plugin_manager_obj")
def pluginmngr_test():
    return PluginManager()

@pytest.fixture
def message():
    return "Test message"


def test_app_endpoint_main():
    client = TestClient(app)
    print(client)
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
async def test_start_plugins():
    plugin_manager = AsyncMock(spec=PluginManager)
    await start_plugins(plugin_manager)
    plugin_manager.load_plugins.assert_called_once()

@pytest.mark.asyncio
async def test_start_bot(listener_obj, plugin_manager_obj):
    start = AsyncMock()
    task = asyncio.create_task(start_bot(listener_obj, plugin_manager_obj))
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        start.assert_awaited
        await task


@pytest.mark.asyncio
async def test_run_bot(caplog):
    start_bot = AsyncMock()
    task = asyncio.create_task(run_bot())
    start_bot.assert_awaited
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_get_latest_message(message):
    listener = Listener()
    assert listener is not None
    assert settings.VALUE == "On Testing"
    await listener.start()
    await listener.handler.handle_message(message)
    assert await listener.handler.get_latest_message() == message


@pytest.mark.asyncio
async def test_listener_handler():
    listener_test = Listener()
    print(listener_test)
    assert listener_test is not None
    assert isinstance(listener_test, Listener)
    await listener_test.start()
    await listener_test.handler.handle_message("hello")
    msg = await listener_test.handler.get_latest_message()
    print(msg)
    assert msg == "hello"


@pytest.mark.asyncio
async def test_baseplugins():
    plugin = BasePlugin
    assert callable(plugin.start) 
    assert callable(plugin.stop)
    assert callable(plugin.send_notification) 
    assert callable(plugin.should_handle)
    assert callable(plugin.handle_message)

