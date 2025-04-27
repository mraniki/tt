import pytest
import os # Import os
from unittest.mock import AsyncMock

# Import tt settings and alias it
from tt.config import settings as tt_settings
# Import myllm settings and alias it
from myllm.config import settings as myllm_settings
# Import myllm's config module to help locate its defaults
import myllm.config as myllm_config_module

from tt.plugins.default_plugins.ai_agent_plugin import AIAgentPlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    print("\nConfiguring settings for [testing] environment in test_ai_agent_plugin.py...")

    # --- Determine Paths ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tt_root = os.path.dirname(current_dir) # Assumes tests/ is one level down from tt project root
    settings_path = os.path.join(tt_root, 'settings.toml') # Main settings from 1P
    talky_settings_path = os.path.join(tt_root, 'tt', 'talky_settings.toml') # tt's defaults
    myllm_default_path = os.path.join(os.path.dirname(myllm_config_module.__file__), 'default_settings.toml') # myllm's internal defaults

    print(f"Located tt settings.toml at: {settings_path}")
    print(f"Located tt talky_settings.toml at: {talky_settings_path}")
    print(f"Located myllm default_settings.toml at: {myllm_default_path}")

    # --- Determine Files to Load ---
    files_to_load_tt = []
    if os.path.exists(talky_settings_path): files_to_load_tt.append(talky_settings_path)
    if os.path.exists(settings_path): files_to_load_tt.append(settings_path)

    files_to_load_myllm = []
    if os.path.exists(myllm_default_path): files_to_load_myllm.append(myllm_default_path)
    if os.path.exists(talky_settings_path): files_to_load_myllm.append(talky_settings_path)
    if os.path.exists(settings_path): files_to_load_myllm.append(settings_path)

    # --- Configure tt's main settings ---
    print(f"Configuring tt_settings with files: {files_to_load_tt}")
    tt_settings.configure(
        FORCE_ENV_FOR_DYNACONF="testing",
        SETTINGS_FILE_FOR_DYNACONF=files_to_load_tt,
        ENVVAR_PREFIX_FOR_DYNACONF="TT"
    )
    print(f"tt.config.settings current_env after config: {tt_settings.current_env}")

    # --- Configure myllm's settings ---
    print(f"Configuring myllm_settings with files: {files_to_load_myllm}")
    myllm_settings.configure(
        FORCE_ENV_FOR_DYNACONF="testing",
        SETTINGS_FILE_FOR_DYNACONF=files_to_load_myllm, # Explicitly load correct files
        ENVVAR_PREFIX_FOR_DYNACONF="TT" # Match prefix
    )
    print(f"myllm.config.settings current_env after config: {myllm_settings.current_env}")

    # Optional: Verify keys exist after loading
    print(f"tt_settings exists('myllm_enabled')? {tt_settings.exists('myllm_enabled')}")
    print(f"myllm_settings exists('myllm_enabled')? {myllm_settings.exists('myllm_enabled')}")
    print(f"Value in myllm_settings: {myllm_settings.get('myllm_enabled')}") # Use .get() for safety in debug print

    print("Settings configuration complete in test_ai_agent_plugin.py.")


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    print("\nCreating AIAgentPlugin instance in test_fixture_plugin...")
    # Use tt_settings here as AIAgentPlugin imports from tt.config
    print(f"Value of tt_settings.myllm_enabled before plugin init: {tt_settings.get('myllm_enabled')}")
    # We can still check myllm_settings for comparison if needed
    print(f"Value of myllm_settings.myllm_enabled before plugin init: {myllm_settings.get('myllm_enabled')}")
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
