from __future__ import annotations

import asyncio
import time
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class AttackStatus(str, Enum):
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


class AttackStateSnapshot(BaseModel):
    """Pydantic V2 schema representing the immutable snapshot of system state."""
    model_config = ConfigDict(from_attributes=True, frozen=True)

    status: AttackStatus = AttackStatus.IDLE
    attack_id: str | None = None
    target: str | None = None
    method: str | None = None
    start_time: float | None = None
    elapsed_seconds: float = 0.0
    stats: dict[str, Any] = Field(default_factory=dict)
    error_detail: str | None = None


class StateManager:
    """Thread-safe Single Source of Truth (SSOT) for MHDDoS-GUI."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._state = AttackStateSnapshot()
        self._subscribers: list[asyncio.Queue[AttackStateSnapshot]] = []

    async def get_state(self) -> AttackStateSnapshot:
        """Return a thread-safe immutable copy of the current state."""
        async with self._lock:
            return self._state

    async def transition(
        self,
        status: AttackStatus,
        *,
        attack_id: str | None = None,
        target: str | None = None,
        method: str | None = None,
        stats: dict[str, Any] | None = None,
        error_detail: str | None = None,
    ) -> AttackStateSnapshot:
        """Atomically transition state and notify all real-time subscribers."""
        async with self._lock:
            current_time = time.time()
            start_time = self._state.start_time

            if status == AttackStatus.RUNNING and self._state.status != AttackStatus.RUNNING:
                start_time = current_time
            elif status in (AttackStatus.IDLE, AttackStatus.STOPPED, AttackStatus.COMPLETED, AttackStatus.ERROR):
                start_time = None

            elapsed = (current_time - start_time) if start_time else 0.0

            self._state = AttackStateSnapshot(
                status=status,
                attack_id=attack_id if attack_id is not None else self._state.attack_id,
                target=target if target is not None else self._state.target,
                method=method if method is not None else self._state.method,
                start_time=start_time,
                elapsed_seconds=elapsed,
                stats=stats if stats is not None else self._state.stats,
                error_detail=error_detail,
            )
            snapshot = self._state

        await self._notify_subscribers(snapshot)
        return snapshot

    async def update_status(
        self,
        status: AttackStatus,
        error_detail: str | None = None,
    ) -> AttackStateSnapshot:
        return await self.transition(status=status, error_detail=error_detail)

    async def set_attack_params(
        self,
        *,
        target: str | None = None,
        duration: int | None = None,
        threads: int | None = None,
        method: str | None = None,
        rpc: int | None = None,
    ) -> AttackStateSnapshot:
        stats_update: dict[str, Any] = {}
        if duration is not None:
            stats_update["duration"] = duration
        if threads is not None:
            stats_update["threads"] = threads
        if rpc is not None:
            stats_update["rpc"] = rpc
        current_stats = self._state.stats.copy() if self._state.stats else {}
        current_stats.update(stats_update)
        return await self.transition(self._state.status, target=target, method=method, stats=current_stats)

    async def _notify_subscribers(self, snapshot: AttackStateSnapshot) -> None:
        for queue in list(self._subscribers):
            try:
                queue.put_nowait(snapshot)
            except asyncio.QueueFull:
                pass

    def subscribe(self) -> asyncio.Queue[AttackStateSnapshot]:
        queue: asyncio.Queue[AttackStateSnapshot] = asyncio.Queue(maxsize=50)
        self._subscribers.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[AttackStateSnapshot]) -> None:
        if queue in self._subscribers:
            self._subscribers.remove(queue)


state_manager = StateManager()
