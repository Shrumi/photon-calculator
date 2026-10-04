"""Триал-логика ФОТОН: 3 минуты с первого запуска.

Состояние — %LOCALAPPDATA%/PhotonCalc/state.json:
накопленное время работы (триал не сбрасывается перезапуском)
и флаг активации ключом.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

TRIAL_SECONDS = 3 * 60

APP_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "PhotonCalc"
STATE_FILE = APP_DIR / "state.json"


def _load() -> dict:
    try:
        return json.loads(STATE_FILE.read_text("utf-8"))
    except Exception:
        return {}


def _save(state: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), "utf-8")


def is_licensed() -> bool:
    return bool(_load().get("licensed"))


def activate(key: str, machine_id: str) -> bool:
    from . import license as lic

    if lic.check_key(lic.normalize_machine_id(machine_id), key):
        state = _load()
        state["licensed"] = True
        state["key"] = key
        _save(state)
        return True
    return False


def trial_state() -> dict:
    """Остаток триала; тикает только пока приложение работает."""
    state = _load()
    if state.get("licensed"):
        return {"licensed": True, "remaining": TRIAL_SECONDS}

    now = int(time.time())
    used = int(state.get("used", 0)) + now - int(state.get("last_seen", now))
    used = max(0, min(used, TRIAL_SECONDS))
    state["used"] = used
    state["last_seen"] = now
    _save(state)
    return {"licensed": False, "remaining": TRIAL_SECONDS - used}


def trial_heartbeat() -> dict:
    """Вызывается UI-ом раз в 5 секунд: тратит триальное время."""
    if is_licensed():
        return {"licensed": True, "remaining": TRIAL_SECONDS}
    state = _load()
    now = int(time.time())
    last = int(state.get("last_seen", now))
    used = int(state.get("used", 0)) + max(0, now - last)
    used = max(0, min(used, TRIAL_SECONDS))
    state["used"] = used
    state["last_seen"] = now
    _save(state)
    return {"licensed": False, "remaining": TRIAL_SECONDS - used, "expired": used >= TRIAL_SECONDS}
