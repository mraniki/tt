import pytest
import asyncio
from tt.utils import MessageProcessor, start_plugins

@pytest.mark.asyncio
async def test_load_plugins():
    message_processor = MessageProcessor()
    message_processor.load_plugins("tt.plugins")

    print("Loaded plugins:", message_processor.plugins)

    assert len(message_processor.plugins) >= 1


@pytest.mark.asyncio
async def test_start_plugins():
    message_processor = MessageProcessor()
    message_processor.load_plugins("tt.plugins")
    
    loop = asyncio.get_running_loop()
    loop.create_task(start_plugins(message_processor))

    assert len(message_processor.plugins) >= 1
    