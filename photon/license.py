"""Лицензионные ключи ФОТОН: оффлайн HMAC-схема.

Ключ = BASE32(HMAC-SHA256(SECRET, payload))[:длина], где payload —
Machine ID (привязка к ПК) или публичная метка (универсальный ключ).
Секрет хранится ТОЛЬКО в генераторе (keygen.py), в приложении — отпечаток.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os

# Секрет генератора: в release-сборке задаётся переменной окружения
# PHOTON_KEYGEN_SECRET, в dev — фиксированный (только для теста).
SECRET_ENV = "PHOTON_KEYGEN_SECRET"
_DEV_SECRET = b"photon-demo-dev-secret-do-not-use-in-prod"

KEY_LEN = 8  # символов ключа (base32, без паддинга)
MAGIC = "PH"


def _secret() -> bytes:
    env = os.environ.get(SECRET_ENV, "").strip()
    return env.encode("utf-8") if env else _DEV_SECRET


def machine_fingerprint(secret: bytes, machine_id: str) -> str:
    """Короткий отпечаток машины для сверки внутри приложения."""
    return base64.b32encode(
        hmac.new(secret, machine_id.encode("utf-8"), hashlib.sha256).digest()
    ).decode("ascii")[:4]


def make_key(machine_id: str) -> str:
    """Ключ, привязанный к Machine ID конкретного ПК."""
    raw = hmac.new(_secret(), f"m:{machine_id}".encode("utf-8"), hashlib.sha256).digest()
    return MAGIC + base64.b32encode(raw).decode("ascii")[:KEY_LEN]


def make_universal_key(label: str = "demo-full") -> str:
    """Универсальный ключ (без привязки к ПК)."""
    raw = hmac.new(_secret(), f"u:{label}".encode("utf-8"), hashlib.sha256).digest()
    return MAGIC + base64.b32encode(raw).decode("ascii")[:KEY_LEN]


def check_key(machine_id: str, key: str) -> bool:
    """Проверка ключа в приложении: обычный или универсальный.

    Machine ID проверяем в обеих формах (с дефисами и без): клиент может
    скопировать ID из письма в любом виде.
    """
    key = (key or "").strip().upper().replace(" ", "").replace("-", "")
    mids = {machine_id, normalize_machine_id(machine_id)} - {""}
    if key and any(make_key(m) == key for m in mids):
        return True
    # Универсальные ключи проверяем перебором известных меток.
    for label in ("demo-full", "shrumi", "photon"):
        if make_universal_key(label) == key:
            return True
    return False


def normalize_machine_id(raw: str) -> str:
    """Machine ID из окна блокировки уже нормализован; страховка."""
    return (raw or "").strip().upper().replace(" ", "").replace("-", "")
