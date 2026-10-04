"""КАЛЬКУЛЯТОР ПРАЙСА «ФОТОН» — демо-версия.

FastAPI-сервер + статический UI. Запуск: python -m photon.app
"""
from __future__ import annotations

import hashlib
import platform
import socket
import threading
import uuid
import webbrowser
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from . import trial
from .catalog import search_services

app = FastAPI(title="ФОТОН — калькулятор прайса (демо)")

STATIC_DIR = Path(__file__).parent / "static"


def machine_id() -> str:
    """Стабильный ID машины: UUID node + hostname, SHA1 → 12 hex → группами."""
    node = uuid.UUID(int=uuid.getnode()).hex
    host = platform.node()
    raw = hashlib.sha1(f"{node}|{host}".encode("utf-8")).hexdigest()[:12].upper()
    return "-".join(raw[i : i + 4] for i in range(0, 12, 4))


class KeyPayload(BaseModel):
    key: str


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/state")
def state() -> dict:
    st = trial.trial_state()
    return {**st, "machine_id": machine_id()}


@app.get("/api/heartbeat")
def heartbeat() -> dict:
    return trial.trial_heartbeat()


@app.post("/api/activate")
def activate(p: KeyPayload) -> dict:
    ok = trial.activate(p.key, machine_id())
    if not ok:
        raise HTTPException(status_code=400, detail="Ключ недействителен")
    return {"ok": True}


@app.get("/api/search")
def search(q: str) -> list[dict]:
    return search_services(q)


def _find_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main() -> None:
    port = _find_port()
    threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
