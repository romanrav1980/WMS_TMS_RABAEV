"""
ws_manager.py — менеджер WebSocket-соединений для /ws/dispatch.

Sprint 96: события реального времени между диспетчерами.
"""

import asyncio
import json
import logging
from typing import Any

from fastapi import WebSocket

log = logging.getLogger(__name__)


class ConnectionManager:
    """Thread-safe менеджер WebSocket-соединений.

    broadcast_sync() вызывается из синхронных endpoint-ов FastAPI;
    он планирует корутину broadcast() на event loop, захваченный при первом connect.
    """

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []
        self._loop: asyncio.AbstractEventLoop | None = None

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                pass
        log.debug("WS connect: total=%d", len(self._connections))

    def disconnect(self, websocket: WebSocket) -> None:
        try:
            self._connections.remove(websocket)
        except ValueError:
            pass
        log.debug("WS disconnect: total=%d", len(self._connections))

    async def broadcast(self, message: dict[str, Any]) -> None:
        if not self._connections:
            return
        text = json.dumps(message, ensure_ascii=False, default=str)
        dead: list[WebSocket] = []
        for ws in list(self._connections):
            try:
                await ws.send_text(text)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    def broadcast_sync(self, message: dict[str, Any]) -> None:
        """Вызвать из синхронного endpoint после успешной мутации."""
        if not self._connections:
            return
        loop = self._loop
        if loop is None or not loop.is_running():
            return
        asyncio.run_coroutine_threadsafe(self.broadcast(message), loop)

    @property
    def connection_count(self) -> int:
        return len(self._connections)


# Синглтон, импортируется в transport.py
ws_manager = ConnectionManager()
