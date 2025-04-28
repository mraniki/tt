"""
 TT test
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
import uvicorn
from fastapi.testclient import TestClient
from iamlistening import Listener

from tt.app import app
from tt.plugins.plugin_manager import PluginManager
from tt.utils.utils import start_bot

import asyncio
import importlib
from tt.config import settings as tt_settings

# Try to import the module for reloading
try:
    import iamlistening.main as iamlistening_main
except ImportError:
    iamlistening_main = None
    print(
        "Warning: Could not import iamlistening.main for reloading "
        "in test_unit_exception."
    )

@pytest.fixture(scope="session", autouse=True)
def set_test_settings_unit_exception():
    print(
        "\nConfiguring settings for [testing] environment "
        "in test_unit_exception.py..."
    )
    common_config = {
        "FORCE_ENV_FOR_DYNACONF": "testing",
        "ENVVAR_PREFIX_FOR_DYNACONF": "TT"
    }
    print("Configuring tt_settings...")
    tt_settings.configure(**common_config)
    tt_settings.reload()
    print(
        f"tt_settings exists('iamlistening_enabled') after reload? "
        f"{tt_settings.exists('iamlistening_enabled')}"
    )
    # Reload the dependent library module
    if iamlistening_main:
        try:
            importlib.reload(iamlistening_main)
            print("Reloaded iamlistening.main")
        except Exception as e:
            print(f"ERROR: Failed to reload iamlistening.main: {e}")
    else:
        print("Skipping reload for iamlistening.main (not imported).")

    print("Settings configuration complete in test_unit_exception.py.")


@pytest.fixture(name="message")
def message_test():
    return "Hello"


def test_app_endpoint_main():
    client = TestClient(app)
    response = client.get("/")
    init = MagicMock(client)
    print(response)
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
    # print(settings)
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
