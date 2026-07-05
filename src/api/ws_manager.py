# src/api/ws_manager.py
from __future__ import annotations

import asyncio
import logging
from typing import Any
from fastapi import WebSocket
from pydantic import BaseModel

from src.core.state_manager import state_manager, AttackStateSnapshot

logger = logging.getLogger("mhddos_gui.ws")


class WSMessage(BaseModel):
    type: str
    payload: dict[str, Any] | AttackStateSnapshot


class ConnectionManager:
    """Production-grade WebSocket manager with concurrent broadcast and auto-reconciliation."""

    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self._clients)}")

        current_state = await state_manager.get_state()
        await self.send_personal_message(
            WSMessage(type="state_reconcile", payload=current_state),
            websocket,
        )

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self._clients)}")

    async def send_personal_message(self, message: WSMessage, websocket: WebSocket) -> None:
        try:
            await websocket.send_json(message.model_dump())
        except Exception as exc:
            logger.warning(f"Failed to send personal message: {exc}")
            await self.disconnect(websocket)

    async def broadcast(self, message: WSMessage) -> None:
        """Concurrent non-blocking broadcast to prevent slow-client lag."""
        async with self._lock:
            target_clients = list(self._clients)

        if not target_clients:
            return

        payload_dict = message.model_dump()
        tasks = [client.send_json(payload_dict) for client in target_clients]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        dead_clients: list[WebSocket] = []
        for client, result in zip(target_clients, results):
            if isinstance(result, Exception):
                logger.warning(f"Removing dead client after broadcast error: {result}")
                dead_clients.append(client)

        if dead_clients:
            async with self._lock:
                for dead in dead_clients:
                    self._clients.discard(dead)


ws_manager = ConnectionManager()
