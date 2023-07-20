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
from tt.utils import send_notification, start_listener, start_plugins

#start_bot, run_bot

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
async def test_baseplugins():
    plugin = BasePlugin
    assert callable(plugin.start) 
    assert callable(plugin.stop)
    assert callable(plugin.send_notification) 
    assert callable(plugin.should_handle)
    assert callable(plugin.handle_message)
