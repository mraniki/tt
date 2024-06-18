from fastapi import FastAPI
from nicegui import ui

from tt.config import settings
from tt.utils.version import __version__


def init(fastapi_app: FastAPI) -> None:
    """
    Frontend component activated via `settings.ui_enabled = True`
    and using https://github.com/zauberzeug/nicegui/

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

    @ui.page("/show")
    def show():
        ui.add_head_html(
            '<link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">'
        )
        with ui.left_drawer(top_corner=True, bottom_corner=True).style(
            "background-color: #d7e3f4"
        ):
            ui.label("LEFT DRAWER")
        ui.label(f"Talky Trader v{__version__}")
        ui.video(
            src=settings.live_tv_url,
            autoplay=True,
        )
        content = """
                    <!-- TradingView Widget BEGIN -->
            <div class="tradingview-widget-container">
            <div class="tradingview-widget-container__widget"></div>
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
                     """ # noqa: E501
        ui.add_body_html(content)
        ui.html(
            """
            <br>
            <p align="left">
            <a href="https://talky.readthedocs.io/"><img src="https://img.shields.io/badge/Wiki-%23000000.svg?style=for-the-badge&logo=wikipedia&logoColor=white"></a>
            <br><a href="https://github.com/mraniki/tt/"><img src="https://img.shields.io/badge/github-%23000000.svg?style=for-the-badge&logo=github&logoColor=white"></a><br>

            """
        )

    ui.run_with(
        fastapi_app,
        title=f"Talky Trader v{__version__}",
        favicon="https://raw.githubusercontent.com/mraniki/tt/main/docs/_static/favicon.png",
    )
