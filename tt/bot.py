"""
TalkyTrader 🪙🗿
"""

import http
import asyncio
import uvicorn
from fastapi import FastAPI, Request

from tt.config import settings, logger
from tt.utils import listener, send_notification, __version__


# ⛓️🤖🙊BOT
app = FastAPI(title="TALKYTRADER")


@app.on_event("startup")
async def start_bot():
    event_loop = asyncio.get_event_loop()
    try:
        event_loop.create_task(listener())
    except Exception as error:
        logger.error(error)


# @app.on_event("shutdown")
# async def shutdown_event():
#     """fastapi shutdown"""
#     logger.info("shutting down")
#     uvicorn.keep_running = False


@app.get("/")
async def root():
    """fastapi root"""
    return __version__


@app.get("/health")
async def health_check():
    """fastapi health"""
    return __version__


@app.post("/webhook", status_code=http.HTTPStatus.ACCEPTED)
async def webhook(request: Request):
    """
    FastAPI '/webhook' endpoint.
    """
    data = await request.json()
    if data["key"] != settings.webhook_secret:
        return {"status": "ERROR"}
    await send_notification(data)
    return {"status": "OK"}


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=int(settings.port))
