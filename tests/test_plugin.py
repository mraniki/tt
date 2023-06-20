import pytest
import asyncio
import ping3
from tt.utils import MessageProcessor, start_plugins
from tt.config import settings
from tt.plugins.example_plugin import ExamplePlugin
from tt.plugins.helper_plugin import HelperPlugin

@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="message_processor")
def message_processor_fixture():
    message_processor = MessageProcessor()
    message_processor.load_plugins("tt.plugins")
    return message_processor


@pytest.mark.asyncio
async def test_load_plugins(message_processor):
    loop = asyncio.get_running_loop()
    loop.create_task(start_plugins(message_processor))
    assert len(message_processor.plugins) >= 1


@pytest.mark.asyncio
async def test_example_plugin(message_processor):
    plugin = ExamplePlugin()
    loop = asyncio.get_running_loop()
    loop.create_task(start_plugins(message_processor))
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
    assert plugin.should_handle("any message") is True


@pytest.mark.asyncio
async def test_trading_switch(message_processor):
    """Test switch """
    plugin = HelperPlugin()
    loop = asyncio.get_running_loop()
    loop.create_task(start_plugins(message_processor))
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_trading}")
    assert settings.trading_enabled == False

# @pytest.mark.asyncio
# async def test_help_command_output(self):
#     output = self.instance.help_command()
#     expected_start = f"{self.instance.version}\n"
#     self.assertTrue(output.startswith(expected_start), f"Output should start with '{expected_start}'")

#     expected_contains = [f"🕸️ {self.instance.host_ip}\n",
#                             f"🏓 {round(ping3.ping(settings.ping, unit='ms'), 3)}\n",
#                             f"{self.instance.help_message}"]
#     for expected in expected_contains:
#         self.assertIn(expected, output, f"Output should contain '{expected}'")