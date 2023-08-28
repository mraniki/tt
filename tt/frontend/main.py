from fastapi import FastAPI
from nicegui import ui

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

    @ui.page("/show", dark=True)
    def show():
        ui.add_head_html(
            '<link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">'
        )
        ui.label("Hello, you are using TT Talky Trader v" + __version__)
        ui.video(
            "https://liveprodusphoenixeast.global.ssl.fastly.net/USPhx-HD/Channel-TX-USPhx-AWS-virginia-1/Source-USPhx-16k-1-s6lk2-BP-07-03-0Yn1cQZHOtP_live.m3u8"  # noqa: E501
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

    ui.run_with(
        fastapi_app,
    )
