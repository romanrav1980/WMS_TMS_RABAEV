"""
vrp_job_store.py — хранилище активных VRP-задач.
Sprint 101: SSE отмена и таймаут.

Только in-memory; при перезапуске API очищается (нормально — задачи короткоживущие).
"""

import asyncio
import threading
import uuid
from dataclasses import dataclass, field
from typing import AsyncGenerator


@dataclass
class VrpJob:
    job_id: str
    cancel_event: threading.Event = field(default_factory=threading.Event)
    done: bool = False
    result: dict | None = None
    error: str | None = None
    events: list[dict] = field(default_factory=list)
    _loop: asyncio.AbstractEventLoop | None = None
    _queue: asyncio.Queue | None = None  # type: ignore[type-arg]

    def put_event(self, event: dict) -> None:
        """Вызывается из sync-потока VRP-решателя."""
        self.events.append(event)
        if self._loop and self._queue and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._queue.put(event), self._loop)

    async def stream(self) -> AsyncGenerator[str, None]:
        """Генератор SSE-событий для GET /planner/solve/{job_id}/stream."""
        import json
        self._loop = asyncio.get_running_loop()
        self._queue = asyncio.Queue()
        # Отдаём уже накопленные события
        for ev in self.events:
            yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        # Затем ждём новых
        while not self.done:
            try:
                ev = await asyncio.wait_for(self._queue.get(), timeout=30.0)
                yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
            except asyncio.TimeoutError:
                yield "data: {\"type\":\"ping\"}\n\n"
        # Финальное событие если ещё не отдали
        if self.result:
            pass  # уже отдано через put_event


class VrpJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, VrpJob] = {}
        self._lock = threading.Lock()

    def create(self) -> VrpJob:
        job = VrpJob(job_id=str(uuid.uuid4()))
        with self._lock:
            self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> VrpJob | None:
        return self._jobs.get(job_id)

    def cancel(self, job_id: str) -> bool:
        job = self.get(job_id)
        if job and not job.done:
            job.cancel_event.set()
            job.done = True
            job.put_event({"type": "cancelled"})
            return True
        return False

    def cleanup_done(self) -> None:
        """Удалить завершённые задачи (вызывать периодически)."""
        with self._lock:
            done = [k for k, v in self._jobs.items() if v.done]
            for k in done:
                del self._jobs[k]


# Синглтон
vrp_job_store = VrpJobStore()
