import os  # Import os
from unittest.mock import AsyncMock

# Import myllm's config module to help locate its defaults
# import myllm.config as myllm_config_module # REMOVED
import pytest

# Import myllm settings and alias it
# from myllm.config import settings as myllm_settings # REMOVED

# Import tt settings and alias it
from tt.config import settings as tt_settings
from tt.plugins.default_plugins.ai_agent_plugin import AIAgentPlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    print(
        "\nConfiguring settings for [testing] environment in "
        "test_ai_agent_plugin.py..."
    )

    # --- REMOVED PATH AND FILE LOADING LOGIC --- 

    # --- Configure tt's main settings ---
    # Use ENVVAR_PREFIX_FOR_DYNACONF to ensure TT_CONFIG_DIR is respected
    tt_settings.configure(
        FORCE_ENV_FOR_DYNACONF="testing",
        ENVVAR_PREFIX_FOR_DYNACONF="TT" # Ensures TT_ settings are loaded
    )
    print(f"tt.config.settings current_env after config: {tt_settings.current_env}")

    # --- REMOVED myllm_settings.configure() --- 

    # Optional: Verify keys exist after loading (using tt_settings)
    print(
        f"tt_settings exists('myllm_enabled')? {tt_settings.exists('myllm_enabled')}"
    )
    # Use .get() for safety in debug print
    print(
        f"Value tt_settings for myllm_enabled: {tt_settings.get('myllm_enabled')}"
    )

    print("Settings configuration complete in test_ai_agent_plugin.py.")


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    print("\nCreating AIAgentPlugin instance in test_fixture_plugin...")
    # Settings should be loaded by the simplified fixture now
    plugin = AIAgentPlugin()
    print("AIAgentPlugin instance created.")
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
