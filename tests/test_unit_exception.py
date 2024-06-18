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
from tt.utils.utils import start_bot


@pytest.fixture(name="message")
def message_test():
    return "Hello"


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
