from time import sleep
from unittest.mock import AsyncMock

import pytest

from tt.config import settings
from tt.plugins.default_plugins.llm_plugin import LlmPlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return LlmPlugin()


@pytest.mark.asyncio
async def test_plugin(plugin):
    """Test message handling"""
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_question}")
    assert plugin.should_handle("any message") is True
    assert plugin.llm is not None
    assert callable(plugin.llm.chat)


@pytest.mark.asyncio
async def test_plugin_notification(plugin):
    """Test notification"""
    plugin.send_notification = AsyncMock()
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_aichat}")
    plugin.send_notification.assert_awaited_once()


@pytest.mark.asyncio
async def test_bot_ignore(plugin):
    msg = "⚠️"
    result = await plugin.handle_message(msg)
    assert result is None


@pytest.mark.asyncio
async def test_parsing_llm(plugin):
    """Test scr"""
    plugin.llm.chat = AsyncMock()
    await plugin.handle_message(
        f"{settings.bot_prefix}{settings.bot_command_aichat} hello"
    )
    plugin.llm.chat.assert_awaited_once()


@pytest.mark.asyncio
async def test_parsing_info(plugin):
    """Test info"""
    plugin.llm.get_info = AsyncMock()
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_info}")
    plugin.llm.get_info.assert_awaited_once()


@pytest.mark.asyncio
async def test_info(plugin):
    """Test info"""
    result = await plugin.llm.get_info()
    assert result is not None


# @pytest.mark.asyncio
# async def test_llm_chat(plugin):
#     """Test llm"""
#     result = await plugin.llm.chat("tell me a story")
#     sleep(20)
#     print(result)
#     assert result is not None


# @pytest.mark.asyncio
# async def test_clear_chat_history(plugin):
#     result = plugin.llm.export_chat_history()
#     assert result is not None
