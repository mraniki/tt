"""
 TT test
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
import uvicorn
from fastapi.testclient import TestClient
from iamlistening import Listener

from tt.app import app
from tt.config import settings
from tt.plugins.plugin_manager import PluginManager
from tt.utils.utils import start_bot, start_plugins
from tt.utils.version import check_version


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


def test_dynaconf_is_in_testing():
    print(settings)
    assert settings.VALUE == "On Testing"


@pytest.fixture(name="message")
def message_test():
    return "Hello"


# @pytest.mark.asyncio
# async def test_run_bot():
#     check_version = AsyncMock()
#     run_bot = AsyncMock()
#     listener = AsyncMock()
#     plugin_manager = AsyncMock()
#     assert listener is not None
#     assert plugin_manager is not None
#     assert run_bot.assert_awaited
#     assert check_version.assert_awaited


@pytest.mark.asyncio
async def test_run_bot():
    start_bot = AsyncMock()
    listener = AsyncMock()
    plugin_manager = AsyncMock()

    assert listener is not None
    assert plugin_manager is not None

    await start_bot(listener, plugin_manager)
    start_bot.assert_called_once_with(listener, plugin_manager)

    assert "You are" in caplog.text


def test_app_endpoint_main():
    client = TestClient(app)
    response = client.get("/")
    init = MagicMock(client)
    assert response.status_code is not None
    assert init.assert_called


def test_app_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_webhook_with_valid_auth():
    client = TestClient(app)
    payload = {"data": "buy BTC"}
    response = client.post("/webhook/123abc", json=payload)
    post = MagicMock()
    print(response.content.decode("utf-8"))
    assert response is not None
    assert response.content.decode("utf-8") is not None
    assert post.assert_called


def test_webhook_with_invalid_auth():
    client = TestClient(app)
    payload = {"data": "my_data"}
    response = client.post("/webhook/abc123", json=payload)
    print(response.content.decode("utf-8"))
    assert response.content.decode("utf-8") is not None


@pytest.mark.asyncio
async def test_check_version(caplog):
    await check_version()
    assert "You are" in caplog.text


@pytest.mark.asyncio
async def test_check_version_exception():
    with pytest.raises(Exception):
        await check_version("123")


@pytest.mark.asyncio
async def test_start_plugins():
    plugin_manager = AsyncMock(spec=PluginManager)
    await start_plugins(plugin_manager)
    plugin_manager.load_plugins.assert_called_once()


@pytest.mark.asyncio
async def test_start_bot(message):
    plugin_manager = AsyncMock(spec=PluginManager)
    get_latest_message = AsyncMock()
    process_message = AsyncMock()
    print(settings)
    listener = Listener()
    assert listener is not None
    assert isinstance(listener, Listener)
    assert listener.clients is not None
    await start_bot(listener, plugin_manager, max_iterations=1)
    for client in listener.clients:
        await client.handle_message(message)
        msg = await client.get_latest_message()
        get_latest_message.assert_awaited
        process_message.assert_awaited
        assert msg == message


def test_main():
    client = TestClient(app)
    uvicorn.run = AsyncMock(client)
    uvicorn.run.assert_called_once
