"""
 TT test
"""
import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from iamlistening import ChatManager, Listener
from iamlistening.platform import TelegramHandler

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

@pytest.fixture(name="ial_test")
def ial_test():
    listener = Listener()
    listener.handler = TelegramHandler()
    return listener

@pytest.fixture(name="plugin_manager_obj")
def pluginmngr_test():
    return PluginManager()

@pytest.fixture
def message():
    return "Test message"

@pytest.fixture
def mock_listener():
   mock_listener = AsyncMock(spec=Listener)
   mock_listener.handler = AsyncMock(spec=ChatManager)
   return mock_listener

@pytest.fixture
def mock_plugin_manager():
   return AsyncMock(spec=PluginManager)

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
async def test_run_bot():
    listener_instance = Listener()
    start_bot = AsyncMock(side_effect=[listener_instance])
    with patch('tt.utils.start_bot', start_bot):
        task = asyncio.create_task(run_bot())
        await asyncio.gather(task, asyncio.sleep(2))
        start_bot.assert_awaited
        listener_created = listener_instance
        assert isinstance(listener_created, Listener) 
        task.cancel()


@pytest.mark.asyncio
async def test_start_bot():
    listener_instance = Listener()
    listener_instance.handler = AsyncMock(spec=ChatManager)
    plugin_manager_instance = PluginManager()
    with patch('iamlistening.Listener', listener_instance):
        with patch('tt.plugins.plugin_manager', plugin_manager_instance):
            task = asyncio.create_task(
            await start_bot(
                listener_instance, 
                plugin_manager_instance,
                max_iterations=1))
            listener_instance.start.assert_awaited_once()
            plugin_manager_instance.start_plugins.assert_awaited() 
            await listener_instance.handler.handle_message("hello")

            try:
                msg = await asyncio.wait_for(
                    listener_instance.handler.get_latest_message(),
                    timeout=1.0)
                assert msg == "hello"
            except TimeoutError:
                pytest.fail("Timeout occurred while waiting for the latest message")

            # listener_instance.handler.get_latest_message.assert_awaited_once() 
            # plugin_manager_instance.process_message.assert_awaited_once()
            asyncio.sleep.assert_awaited_with(1)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task

# await listener_instance.handler.handle_message("hello")
# msg = await listener_instance.handler.get_latest_message()
# print(msg)
# assert msg == "hello"

@pytest.mark.asyncio
async def test_baseplugins():
    plugin = BasePlugin
    assert callable(plugin.start) 
    assert callable(plugin.stop)
    assert callable(plugin.send_notification) 
    assert callable(plugin.should_handle)
    assert callable(plugin.handle_message)
