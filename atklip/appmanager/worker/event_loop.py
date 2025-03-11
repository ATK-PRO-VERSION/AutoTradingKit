# ruff: noqa: D100, D101, D102, D103, D104, D107
from __future__ import annotations
import threading
from typing import Coroutine

import asyncio,os
from asyncio import run
from PySide6.QtCore import QObject, Signal, QRunnable, Slot, QThreadPool


class LoopThread(threading.Thread):
    def __init__(self: LoopThread) -> None:
        super().__init__()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def run(self: LoopThread) -> None:
        self.loop.run_forever()

    def stop(self: LoopThread) -> None:
        asyncio.set_event_loop(None)
        self.loop.call_soon_threadsafe(self.loop.stop)

    def create_task(self: LoopThread, coro: Coroutine) -> None:
        self.loop.call_soon_threadsafe(self.loop.create_task, coro)

