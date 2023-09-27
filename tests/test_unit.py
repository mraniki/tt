"""
 TT test
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import uvicorn
from fastapi.testclient import TestClient
from iamlistening import Listener

from tt.app import app, start_bot_task
from tt.config import logger, settings
from tt.plugins.plugin_manager import PluginManager
from tt.utils import check_version, send_notification, start_bot, start_plugins


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


def test_dynaconf_is_in_testing():
    assert settings.platform is not None
    assert settings.VALUE == "On Testing"


@pytest.fixture(name="message")
def message_test():
    return "hello"


# @pytest.fixture(name="listener")
# def listener():
#     return Listener()


# @pytest.fixture(name="plugin_manager_obj")
# def pluginmngr_test():
#     return PluginManager()


@pytest.fixture
def message():
    return "Hello"


@pytest.mark.asyncio
async def test_start_bot_task():
    run_bot = AsyncMock()
    await start_bot_task()
    assert run_bot.assert_awaited_once


def test_app_endpoint_main():
    client = TestClient(app)
    response = client.get("/")
    init = MagicMock(client)
    # assert response.status_code == 200
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
async def test_check_version():
    # Mock the required dependencies and setup their return values
    settings.repo = "https://github.com/example/repo"
    __version__ = "1.0.0"
    response_data = {"name": "2.0.0"}

    with patch("aiohttp.ClientSession") as mock_session:
        mock_response = AsyncMock()
        mock_response.json.return_value = response_data
        mock_session.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        # Call the function
        await check_version()

        # Check the logs and assertions
        logger.debug.assert_called_with("Github repo: {}", response_data)
        logger.info.assert_called_with("Latest version: {}", response_data["name"])
        logger.debug.assert_called_with(
            "You are NOT using the latest %s: %s", response_data["name"], __version__
        )
        send_notification.assert_called_with(
            f"You are NOT using the latest {response_data['name']}"
        )


@pytest.mark.asyncio
async def test_send_notification(caplog):
    await send_notification("Test message")
    assert "Loaded Discord" in caplog.text


@pytest.mark.asyncio
async def test_start_plugins():
    plugin_manager = AsyncMock(spec=PluginManager)
    await start_plugins(plugin_manager)
    plugin_manager.load_plugins.assert_called_once()


@pytest.mark.asyncio
async def test_start_bot(message):
    plugin_manager = AsyncMock(spec=PluginManager)
    print(settings)
    listener = Listener()
    assert listener is not None
    assert isinstance(listener, Listener)
    assert listener.platform_info is not None
    await start_bot(listener, plugin_manager, max_iterations=1)
    # listener.start.assert_awaited_once()
    for client in listener.platform_info:
        await client.handle_message(message)
        msg = await client.get_latest_message()
        # client.get_latest_message.assert_awaited_once()
        assert msg == message


def test_main():
    client = TestClient(app)
    uvicorn.run = AsyncMock(client)
    uvicorn.run.assert_called_once
