"""
TalkyTrader 🪙🗿
================

Bot Launcher and API

Talky Trader is an app
built with FastAPI
https://github.com/tiangolo/fastapi

It allows you to connect
to a messaging chat platform
to interact with trading module.

"""
import asyncio
from contextlib import asynccontextmanager

import requests
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from tt.config import logger, settings
from tt.utils import __version__, run_bot, send_notification


@asynccontextmanager
async def lifespan(app):
    """
    An asynchronous context manager
    that manages the lifespan of the application.

    Parameters:
    - app: The application to manage the lifespan of.

    Returns:
    - None

    This function creates an event loop,
    starts a task to run the bot, and yields control to the caller.
    The caller is responsible for cleaning up any
    resources after the lifespan of the
    application has ended.
    """
    logger.debug("Starting...")
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(run_bot())
    yield
    logger.debug("Closing...")


app = FastAPI(lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Get the root endpoint.

    Returns:
        HTMLResponse: The HTML response

    Note:
        If `settings.ui_enabled` is `True`,
        user will be redirected to
        the UI frontend
    """
    if settings.ui_enabled:
        from tt.frontend.main import init

        init(app)
        return RedirectResponse(url="/show")
    return __version__


@app.get("/health")
async def health_check():
    """
    End point to know if
    the API is up and running
    """
    return __version__


@app.post(f"/webhook/{settings.webhook_secret}", status_code=202)
async def webhook(request: Request):
    """
    Webhook endpoint to receive webhook requests
    with option to forward the data to another endpoint.
    Webhook endpoint to
    send order signal generated
    via http://tradingview.com
    or anyother platform.
    Endpoint is
    :file:`/webhook/{settings.webhook_secret}`
    so in trading view you can add:
    https://YOURIPorDOMAIN/webhook/123456
    """
    data = await request.body()
    logger.debug("Webhook request received {}", data)
    await send_notification(data)

    if settings.forwarder:
        logger.debug("Forwarding {} to {}", data, str(settings.forwarder_url))
        requests.post(
            settings.forwarder_url, data, headers={"Content-Type": "application/json"}
        )

    return {"status": "OK"}


if __name__ == "__main__":
    """
    This line runs the Uvicorn server with the specified host and port.
    The `app` variable is an instance of the FastAPI application,
    and the `settings.host` and `settings.port` variables
    are the host and port to run the server on, respectively
    More Info https://github.com/encode/uvicorn
    """
    uvicorn.run(
        app,
        host=settings.host,
        port=int(settings.port),
        log_level="critical",
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
