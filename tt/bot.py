"""
TalkyTrader 🪙🗿
====================
Bot Launcher and API
"""

import asyncio

import requests
import uvicorn
from fastapi import FastAPI, Request

from tt.config import settings
from tt.utils import __version__, run_bot, send_notification

app = FastAPI(title="TALKYTRADER")


@app.on_event("startup")
async def start_bot_task():
    """⛓️🤖BOT"""
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(run_bot())

@app.get("/")
async def root():
    """fastapi root"""
    return __version__


@app.get("/health")
async def health_check():
    """ health check """
    return __version__


@app.post(f"/webhook/{settings.webhook_secret}", status_code=202)
async def webhook(request: Request):
    """ 
    Webhook endpoint to receive webhook requests
    with option to forward the data to another endpoint.
    """
    data = await request.body()
    await send_notification(data)

    if settings.forwarder:
        requests.post(settings.forwarder_url, data)

    return {"status": "OK"}


if __name__ == "__main__":
    """ 
    This line runs the Uvicorn server with the specified host and port.
    The `app` variable is an instance of the FastAPI application, 
    and the `settings.host` and `settings.port` variables 
    are the host and port to run the server on, respectively
    """ 
    uvicorn.run(
        app,
        host=settings.host,
        port=int(settings.port),)

