def test_listener():
    async def mock_run_forever():
        pass

    async def mock_get_latest_message():
        return None

    async def mock_process_message(msg):
        pass

    async def mock_start_all_plugins():
        pass

    Listener.run_forever = mock_run_forever
    Listener.get_latest_message = mock_get_latest_message
    MessageProcessor.process_message = mock_process_message
    MessageProcessor.start_all_plugins = mock_start_all_plugins

    import asyncio
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(listener())
    except Exception as error:
        assert False, f"listener test failed: {error}"
    finally:
        loop.close()