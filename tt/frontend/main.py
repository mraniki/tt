from fastapi import FastAPI
from nicegui import ui

from tt.config import settings
from tt.utils import __version__


def init(fastapi_app: FastAPI) -> None:
    """
    Initializes the UI for the provided `fastapi_app` instance.

    Parameters:
        fastapi_app (FastAPI): The FastAPI application instance to be initialized.

    Returns:
        None

    Note:
        This function defines a nested function `show` which is decorated
        with `@ui.page("/show", dark=True)`.
        The `show` function displays a label and a video using the `ui.label`
        and `ui.video` functions respectively.
        It also includes an HTML content that embeds a TradingView widget.
        The `ui.html` function is used to display the HTML content.

        Finally, the `ui.run_with` function is called to run the
        FastAPI application with the provided `fastapi_app` instance.
    """

    @ui.page("/show")  # , dark=True)
    def show():
        ui.add_head_html(f"<title>Talky Trader v{__version__}</title>")
        ui.add_head_html(
            '<link href="https://raw.githubusercontent.com/mraniki/tt/main/docs/_static/favicon.ico" rel="shortcut icon">'  # noqa: E501
        )
        ui.add_head_html(
            '<link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">'
        )
        ui.label(f"Talky Trader v{__version__}")
        ui.video(
            src=settings.live_tv_url,
            autoplay=True,
        )
        content = """
                    <!-- TradingView Widget BEGIN -->
            <div class="tradingview-widget-container">
            <div class="tradingview-widget-container__widget"></div>
            <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank"><span class="blue-text">Track all markets on TradingView</span></a></div>
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
            {
            "symbols": [
                {
                "proName": "FOREXCOM:SPXUSD",
                "title": "S&P 500"
                },
                {
                "proName": "FX_IDC:EURUSD",
                "title": "EUR to USD"
                },
                {
                "proName": "BITSTAMP:BTCUSD",
                "title": "Bitcoin"
                },
                {
                "proName": "BITSTAMP:ETHUSD",
                "title": "Ethereum"
                }
            ],
            "showSymbolLogo": true,
            "colorTheme": "dark",
            "isTransparent": false,
            "displayMode": "compact",
            "locale": "en"
            }
            </script>
            </div>
            <!-- TradingView Widget END -->
                     """  # noqa: E501
        ui.add_body_html(content)
        with ui.row().classes("w-full items-center"):
            result = ui.label().classes("mr-auto")
            with ui.button(icon="menu"):
                with ui.menu() as menu:
                    ui.menu_item(
                        "Wiki", lambda: result.set_text("https://talky.readthedocs.io")
                    )
                    ui.menu_item(
                        "Github",
                        lambda: result.set_text("https://github.com/mraniki/tt"),
                    )
                    ui.separator()
                    ui.menu_item("Exchanges", lambda: result.set_text("Exchanges"))
                    ui.menu_item("Chat Platform", lambda: result.set_text("Chat"))
                    ui.menu_item("Settings", lambda: result.set_text("Settings"))

    ui.run_with(
        fastapi_app,
    )
