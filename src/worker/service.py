# src/worker/service.py
from __future__ import annotations

import asyncio
import logging
import subprocess
import sys
from typing import Any

from src.core.state_manager import state_manager, AttackStatus
from src.api.ws_manager import ws_manager, WSMessage

logger = logging.getLogger("mhddos_gui.worker")


class WorkerService:
    """Manages background MHDDoS CLI process execution and syncs state to StateManager and WebSocket."""

    def __init__(self) -> None:
        self._process: asyncio.subprocess.Process | None = None
        self._monitor_task: asyncio.Task[None] | None = None
        self._lock = asyncio.Lock()

    async def start_attack(self, target: str, duration: int, threads: int, method: str = "GET", rpc: int = 100) -> None:
        async with self._lock:
            if self._process is not None and self._process.returncode is None:
                raise RuntimeError("An attack is already running.")

            cmd = [
                sys.executable, "-m", "mhddos_gui.cli",
                "--target", target,
                "--duration", str(duration),
                "--threads", str(threads),
                "--method", method,
                "--rpc", str(rpc)
            ]
            logger.info(f"Starting attack process: {' '.join(cmd)}")

            try:
                self._process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            except Exception as exc:
                logger.error(f"Failed to spawn attack process: {exc}")
                await state_manager.update_status(AttackStatus.ERROR, str(exc))
                await self._broadcast_state()
                raise

            await state_manager.set_attack_params(
                target=target,
                duration=duration,
                threads=threads,
                method=method,
                rpc=rpc,
            )
            await state_manager.update_status(AttackStatus.RUNNING)
            await self._broadcast_state()

            self._monitor_task = asyncio.create_task(self._monitor_process(self._process))

    async def stop_attack(self) -> None:
        async with self._lock:
            if self._process is None or self._process.returncode is not None:
                logger.warning("No running attack process to stop.")
                return

            logger.info(f"Terminating attack process tree (PID: {self._process.pid})...")
            await self._terminate_process_tree(self._process.pid)
            
            try:
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning("Process did not exit in time after termination command.")
            
            self._process = None

            if self._monitor_task and not self._monitor_task.done():
                self._monitor_task.cancel()
                try:
                    await self._monitor_task
                except asyncio.CancelledError:
                    pass
            self._monitor_task = None

        await state_manager.update_status(AttackStatus.STOPPED)
        await self._broadcast_state()

    async def _monitor_process(self, proc: asyncio.subprocess.Process) -> None:
        try:
            returncode = await proc.wait()
            async with self._lock:
                if self._process is proc:
                    self._process = None
            
            if returncode == 0:
                logger.info("Attack process completed successfully.")
                await state_manager.update_status(AttackStatus.COMPLETED)
            else:
                logger.error(f"Attack process exited with unexpected code {returncode}.")
                await state_manager.update_status(AttackStatus.ERROR, f"Process exited with code {returncode}")
            
            await self._broadcast_state()
        except asyncio.CancelledError:
            logger.debug("Process monitor task cancelled.")
        except Exception as exc:
            logger.exception(f"Error monitoring attack process: {exc}")
            await state_manager.update_status(AttackStatus.ERROR, str(exc))
            await self._broadcast_state()

    async def _terminate_process_tree(self, pid: int) -> None:
        """Windows-resilient process tree termination."""
        if sys.platform == "win32":
            try:
                kill_proc = await asyncio.create_subprocess_exec(
                    "taskkill", "/F", "/T", "/PID", str(pid),
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                await kill_proc.wait()
            except Exception as exc:
                logger.error(f"taskkill failed for PID {pid}: {exc}")
        else:
            try:
                import os
                import signal
                os.killpg(os.getpgid(pid), signal.SIGTERM)
            except Exception as exc:
                logger.error(f"SIGTERM failed for PID {pid}: {exc}")

    async def _broadcast_state(self) -> None:
        state = await state_manager.get_state()
        await ws_manager.broadcast(WSMessage(type="state_update", payload=state))


worker_service = WorkerService()
