"""
 TT test
"""
import pytest
from bot import parse_message, __version__


@pytest.mark.asyncio
async def test_parse_message():
    # Test help command
    # msg = "/help"
    # help_message = """
    # 🏦 <code>/bal</code>
    # 📦 <code>buy BTCUSDT</code>
    # 🔀 <code>/trading</code>"""
    # bot_menu_help = f"{__version__}\n{help_message}"
    # assert await parse_message(msg) == bot_menu_help

    # # Test trading switch command
    # msg = "/trading"
    # assert await parse_message(msg) == "Trading switch toggled."

    # # Test balance command
    # msg = "/bal"
    # assert await parse_message(msg) == "Your account balance is $1000."

    # # Test position command
    # msg = "/pos"
    # assert await parse_message(msg) == "Your current position is long 10 shares of AAPL."

    # # Test restart command
    # msg = "/restart"
    # assert await parse_message(msg) == "Bot restarted successfully."

    # Test invalid command
    msg = "!foo"
    assert await parse_message(msg) is None

    # Test message to ignore
    msg = "hello world"
    assert await parse_message(msg) is None


    # # Test order message
    # msg = "buy EURUSD sl=1.2 tp=1.5 q=2"
    # assert await parse_message(msg) == ("Order executed:
    #  buy 5 shares of MSFT at $250.")

# import pytest
# from unittest.mock import AsyncMock, patch
# from bot import parse_message

# # Define sample input messages and expected responses
# help_msg = "!help"
# trading_msg = "!trading"
# bal_msg = "!bal"
# pos_msg = "!pos"
# restart_msg = "!restart"
# invalid_msg = "!invalid"
# order_msg = "buy EURUSD 1.0 SL 1.2 TP 1.5"

# expected_help_resp = "Help message"
# expected_trading_resp = "Trading message"
# expected_bal_resp = "Account balance message"
# expected_pos_resp = "Account position message"
# expected_restart_resp = "Restart message"
# expected_order_resp = "Execute order message"

# # Define mock functions for the async functions called in the parse_message() function
# async def mock_help_command():
#     return expected_help_resp

# async def mock_trading_switch_command():
#     return expected_trading_resp

# async def mock_account_balance_command():
#     return expected_bal_resp

# async def mock_account_position_command():
#     return expected_pos_resp

# async def mock_restart_command():
#     return expected_restart_resp

# async def mock_execute_order(action, instrument, stop_loss, take_profit, quantity):
#     return expected_order_resp

# async def mock_notify(response):
#     pass

# @pytest.mark.asyncio
# async def test_parse_message_help():
#     with patch('my_module.help_command', new=AsyncMock(side_effect=mock_help_command)):
#         resp = await parse_message(help_msg)
#         assert resp == expected_help_resp

# @pytest.mark.asyncio
# async def test_parse_message_trading():
#     with patch('my_module.trading_switch_command', new=AsyncMock(side_effect=mock_trading_switch_command)):
#         resp = await parse_message(trading_msg)
#         assert resp == expected_trading_resp

# @pytest.mark.asyncio
# async def test_parse_message_bal():
#     with patch('my_module.account_balance_command', new=AsyncMock(side_effect=mock_account_balance_command)):
#         resp = await parse_message(bal_msg)
#         assert resp == expected_bal_resp

# @pytest.mark.asyncio
# async def test_parse_message_pos():
#     with patch('my_module.account_position_command', new=AsyncMock(side_effect=mock_account_position_command)):
#         resp = await parse_message(pos_msg)
#         assert resp == expected_pos_resp

# @pytest.mark.asyncio
# async def test_parse_message_restart():
#     with patch('my_module.restart_command', new=AsyncMock(side_effect=mock_restart_command)):
#         resp = await parse_message(restart_msg)
#         assert resp == expected_restart_resp

# @pytest.mark.asyncio
# async def test_parse_message_invalid():
#     with patch('my_module.logger.warning') as mock_warning:
#         resp = await parse_message(invalid_msg)
#         assert resp is None
#         mock_warning.assert_called_once_with("invalid command: %s", invalid_msg[1:])

# @pytest.mark.asyncio
# async def test_parse_message_order():
#     fmo_mock = AsyncMock()
#     fmo_mock.get_order.return_value = {"action": "buy", "instrument": "EURUSD", "stop_loss": 1.2, "take_profit": 1.5, "quantity": 1.0}
#     with patch('my_module.FindMyOrder', return_value=fmo_mock):
#         with patch('my_module.execute_order', new=AsyncMock(side_effect=mock_execute_order)):
#             with patch('my_module.notify', new=AsyncMock(side_effect=mock_notify)):
#                 resp = await parse_message(order_msg)
#                 assert resp == expected_order_resp
