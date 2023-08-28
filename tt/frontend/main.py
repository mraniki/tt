from fastapi import FastAPI
from nicegui import app, ui


def init(fastapi_app: FastAPI) -> None:
    @ui.page("/", dark=True)
    def show():
        ui.label("Hello")
        ui.video(
            "https://liveprodusphoenixeast.global.ssl.fastly.net/USPhx-HD/Channel-TX-USPhx-AWS-virginia-1/Source-USPhx-16k-1-s6lk2-BP-07-03-0Yn1cQZHOtP_live.m3u8"
        )

    ui.run_with(
        fastapi_app,
        storage_secret="pick",
    )
