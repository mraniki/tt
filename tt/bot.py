"""
TalkyTrader 🪙🗿
====================
Bot Launcher and API
"""

import asyncio
import uvicorn
from fastapi import FastAPI, Request

from tt.config import settings
from tt.utils import start_bot, send_notification, __version__

app = FastAPI(title="TALKYTRADER")


@app.on_event("startup")
async def start_bot_task():
    """⛓️🤖🙊BOT"""
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(start_bot())

@app.get("/")
async def root():
    """fastapi root"""
    return __version__


@app.get("/health")
async def health_check():
    """fastapi health"""
    return __version__


@app.post(f"/webhook/{settings.webhook_secret}", status_code=202)
async def webhook(request: Request):
    """
    FastAPI '/webhook' endpoint.
    """
    data = await request.body()
    await send_notification(data)
    return {"status": "OK"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=int(settings.port))
