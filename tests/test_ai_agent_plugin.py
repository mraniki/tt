import os  # Import os
from unittest.mock import AsyncMock
import pytest
import importlib # Keep importlib if needed elsewhere, remove if only for fixture
from tt.config import settings as tt_settings # Keep tt_settings if needed
from tt.plugins.default_plugins.ai_agent_plugin import AIAgentPlugin

# Remove module import attempt for reloading
# try:
#     import myllm.main as myllm_main
# except ImportError:
#     myllm_main = None
#     print("Warning: Could not import myllm.main...")

# Remove local set_test_settings_ai_agent fixture
# @pytest.fixture(scope="session", autouse=True)
# def set_test_settings_ai_agent():
#     ...

@pytest.fixture(name="plugin")
def test_fixture_plugin(): # Removed set_test_settings dependency
    """Fixture to create an AIAgentPlugin instance with test settings."""
    # AIAgentPlugin will now use the globally modified tt_settings
    plugin = AIAgentPlugin()
    return plugin


@pytest.mark.asyncio
async def test_plugin(plugin):
    """Test message handling"""
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_aichat}")
    assert plugin.ai_agent is not None
    assert callable(plugin.ai_agent.chat)


@pytest.mark.asyncio
async def test_plugin_notification(plugin):
    """Test notification"""
    plugin.send_notification = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_aichat}")
    plugin.send_notification.assert_awaited_once()


@pytest.mark.asyncio
async def test_bot_ignore(plugin):
    msg = "⚠️"
    result = await plugin.handle_message(msg)
    assert result is None


@pytest.mark.asyncio
async def test_parsing_ai_agent(plugin):
    """Test scr"""
    plugin.ai_agent.chat = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_aichat} hello")
    plugin.ai_agent.chat.assert_awaited_once()


@pytest.mark.asyncio
async def test_parsing_info(plugin):
    """Test info"""
    plugin.ai_agent.get_info = AsyncMock()
    await plugin.handle_message(f"{plugin.bot_prefix}{plugin.bot_command_info}")
    plugin.ai_agent.get_info.assert_awaited_once()


@pytest.mark.asyncio
async def test_info(plugin):
    """Test info"""
    result = await plugin.ai_agent.get_info()
    assert result is not None


@pytest.mark.asyncio
async def test_parsing_switch(plugin):
    """Test switch"""
    result = await plugin.ai_agent_switch_command()
    assert result is not None
    assert "AI Agent is" in result
    assert plugin.ai_agent_mode is True


# @pytest.mark.asyncio
# async def test_llm_chat(plugin):
#     """Test llm chat"""
#     result = await plugin.ai_agent.chat("tell me a story")
#     sleep(10)
#     print(result)
#     assert result is not None


# @pytest.mark.asyncio
# async def test_clear_chat_history(plugin):
#     result = plugin.ai_agent.export_chat_history()
#     assert result is not None
