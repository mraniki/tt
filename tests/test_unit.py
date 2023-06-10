"""
 TT test
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from iamlistening import Listener

# from config import settings, logger
from src.config import settings

from src.bot import (
    load_exchange, parse_message,
    execute_order, trading_switch_command,
    init_message, notify,
    get_name, get_host_ip,
    get_quote, get_trading_asset_balance,
    get_account_balance, app,
    get_ping, get_account, post_init,
    get_account_position, get_account_margin,
    # restart_command,
)


@pytest.fixture
def mock_settings_cex():
    class Settings:
        cex_name = 'binance'
        cex_api = 'api_key'
        cex_secret = 'secret_key'
        cex_password = 'password'
        cex_defaulttype = 'spot'
        cex_testmode = False
        dex_chain_id = ''
    return Settings()

@pytest.fixture
def mock_settings_dex():
    class Settings:
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
        settings.dex_private_key = "0xdeadbeet"
        settings.dex_rpc = "https://eth.llamarpc.com"
        settings.dex_chain_id = 1
        settings.cex_name = ""
        settings.trading_enabled = True
    return Settings()

@pytest.fixture
def mock_discord():
    """Fixture to create an listener object for testing."""
    class Settings:
        settings.discord_webhook_id = "12345678901"
        settings.discord_webhook_token = "1234567890"
        settings.bot_token = "test_bot_token"
        settings.bot_channel_id = "1234567890"
        settings.ping = "8.8.8.8"
    return Settings()

@pytest.fixture
def mock_telegram():
    """Fixture to create an listener object for testing."""
    class Settings:
        settings.telethon_api_id = "123456789"
        settings.telethon_api_hash = "123456789"
        settings.bot_token = "test_bot_token"
        settings.bot_channel_id = "1234567890"
    return Settings()

@pytest.fixture
def mock_matrix_():
    """Fixture to create an listener object for testing."""
    class Settings:
        settings.matrix_hostname = "https://matrix.org"
        settings.matrix_user = "@thismock:matrix.org"
        settings.matrix_pass = "1234"
        settings.bot_token = "token_123435"
        settings.bot_channel_id = "1234567890"
    return Settings()

@pytest.fixture
def message():
    return "hello"

@pytest.fixture
def command_message():
    return "/help"

@pytest.fixture
def order_params():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'EURUSD',
        'quantity': 1,
        # other order parameters
    }

@pytest.mark.asyncio
@pytest.mark.parametrize('msg, expected_output', [
    ('/help', 'help message'),
])
async def test_parse_message(msg, expected_output, mocker):
    """Test parse_message function """
    notify_mock = mocker.patch('src.bot.notify')
    await parse_message(msg)
    if msg == '/help':
        init_mock = mocker.patch('src.bot.init_message', return_value='help message')
        expected_output = 'help message\nhelp init message'
        await parse_message(msg)
        assert '🏦' in notify_mock.call_args[0][0]


@pytest.mark.asyncio
async def test_parse_bal(mock_settings_dex):
    """Test parse_message balance """
    notify_mock = AsyncMock()
    with patch('src.bot.notify',notify_mock):
        await load_exchange()
        await parse_message('/bal')
        assert '🏦' in notify_mock.call_args[0][0]


@pytest.mark.asyncio
async def test_parse_trading(mock_settings_dex):
    """Test parse_message balance """
    notify_mock = AsyncMock()
    with patch('src.bot.notify',notify_mock):
        await load_exchange()
        await parse_message('/trading')
        assert 'Trading is' in notify_mock.call_args[0][0]


@pytest.mark.asyncio
async def test_notify(mock_discord):
    """Test notify function"""
    # Mock Apprise class 
    apprise_mock = MagicMock()
    apprise_instance_mock = AsyncMock()
    apprise_instance_mock.async_notify.return_value = True

    # Test message
    message = '<code>test message</code>'

    # Test with Discord webhook
    with patch('apprise.Apprise', apprise_mock):
        with patch('src.config.settings', mock_discord):
            apprise_mock.return_value = apprise_instance_mock
            output = await notify(message)
            apprise_mock.assert_called_once()
            apprise_instance_mock.add.assert_called_with(
                'discord://12345678901/1234567890')
            apprise_instance_mock.async_notify.assert_called_with(
                body='`test message`', body_format='html')
    # Test with empty message
    output = await notify(None)
    assert output is None

    
@pytest.mark.asyncio
async def test_get_host_ip():
    """Test get_host_ip """
    output = get_host_ip()
    assert output is not None


@pytest.mark.asyncio
async def test_def_get_ping(mock_discord):
    """Test get_ping function """
    output = get_ping(host=8.8.8.8)
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_load_exchange(mock_settings_dex):
    """test exchange dex"""
    exchange = await load_exchange()
    print(exchange)
    assert exchange is not None

@pytest.mark.asyncio
async def test_failed_execute_order(caplog, order_params,mock_settings_dex):
    exchange = await load_exchange()
    trade_confirmation = await execute_order(order_params)
    assert 'Order execution failed' in caplog.text


@pytest.mark.asyncio
async def test_get_quote(mock_settings_dex):
    """Test get_quote """
    await load_exchange()
    output = await get_quote("WBTC")
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_get_name(mock_settings_dex):
    """Test get_name function."""
    await load_exchange()
    output = await get_name()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_get_account_balance(mock_settings_dex):
    """Test get_account_balance."""
    await load_exchange()
    output = await get_account_balance()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_get_trading_asset_balance(mock_settings_dex):
    """Test get_asset_trading_balance."""
    await load_exchange()
    output = await get_trading_asset_balance()
    print(output)
    assert output is not None

    
@pytest.mark.asyncio
async def test_get_account_position(mock_settings_dex):
    """Test get_account_positions."""
    await load_exchange() 
    output = await get_account_position()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_get_account_margin(mock_settings_dex):
    """Test get_account_margin """
    await load_exchange() 
    output = await get_account_margin()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_init_message(mock_settings_dex):
    """Test test_init_message."""
    await load_exchange()
    output = await init_message()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_toggle_trading_active(mock_settings_dex):
    print(settings.trading_enabled)
    await trading_switch_command()
    print(settings.trading_enabled)
    assert settings.trading_enabled is False


@pytest.mark.asyncio
async def test_listener(mock_discord):
    listener = Listener()
    print(listener)
    assert listener is not None


@pytest.mark.asyncio
async def test_message_listener(mock_telegram, message):
    listener = Listener()
    print(listener)
    assert listener is not None
    await listener.handle_message(message)
    # Call the function to be tested
    msg = await listener.get_latest_message()
    print(msg)
    assert msg == "hello"


def test_read_main():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    #assert response.json() == {"msg": "Hello World"}

#@pytest.mark
def test_webhook_with_valid_payload():
    client = TestClient(app)
    payload = {"key": "my_secret_key", "data": "my_data"}
    response = client.post("/webhook", json=payload)
    assert response is not None


# def test_webhook_with_invalid_payload():
#     client = TestClient(app)
#     payload = {"key": "wrong_key", "data": "my_data"}
#     response = client.post("/webhook", json=payload)
#     assert response.json() == {"message": "Key is incorrect"}