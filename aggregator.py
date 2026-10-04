"""IMAP-агрегатор запросов ключей ФОТОН (Яндекс.Почта).

Читает входящие по теме «Запрос ключа ФОТОН», достаёт Machine ID из тела,
печатает готовый ключ для ответа. Запуск (PowerShell):

    $env:PHOTON_IMAP_USER="shrumi@yandex.ru"
    $env:PHOTON_IMAP_APP_PASSWORD="<пароль приложения>"
    python aggregator.py

Пароль приложения: https://id.yandex.ru/security/app-passwords
"""
from __future__ import annotations

import email
import imaplib
import os
import re

from photon.license import make_key

IMAP_HOST = "imap.yandex.ru"
SUBJECT_PATTERN = "Запрос ключа ФОТОН"
SUBJECT_RE = re.compile(r"запрос\s+ключа\s+фотон", re.IGNORECASE)
MID_RE = re.compile(r"([0-9A-F]{4}(?:-[0-9A-F]{4}){2,3})", re.IGNORECASE)


def _decode_header_value(raw: str | None) -> str:
    if not raw:
        return ""
    parts = email.header.decode_header(raw)
    out = []
    for text, charset in parts:
        if isinstance(text, bytes):
            out.append(text.decode(charset or "utf-8", errors="replace"))
        else:
            out.append(text)
    return "".join(out)


def _extract_body(msg: email.message.Message) -> str:
    payload = b""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True) or b""
        charset = msg.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace")
    return ""


def fetch_requests(limit: int = 20) -> list[tuple[str, str]]:
    """Возвращает [(от кого, machine_id)] из непрочитанных писем-запросов."""
    user = os.environ.get("PHOTON_IMAP_USER", "").strip()
    pwd = os.environ.get("PHOTON_IMAP_APP_PASSWORD", "").strip()
    if not user or not pwd:
        raise SystemExit(
            "Задайте переменные окружения PHOTON_IMAP_USER и PHOTON_IMAP_APP_PASSWORD"
        )

    imap = imaplib.IMAP4_SSL(IMAP_HOST)
    imap.login(user, pwd)
    imap.select("INBOX", readonly=True)

    typ, data = imap.search(None, "UNSEEN")
    if typ != "OK":
        return []

    out: list[tuple[str, str]] = []
    for num in data[0].split()[-limit:]:
        typ, msg_data = imap.fetch(num, "(RFC822)")
        if typ != "OK" or not msg_data or not msg_data[0]:
            continue
        msg = email.message_from_bytes(msg_data[0][1])
        subject = _decode_header_value(msg.get("Subject", ""))
        if not SUBJECT_RE.search(subject):
            continue
        from_ = _decode_header_value(msg.get("From", ""))
        m = MID_RE.search(_extract_body(msg))
        if m:
            out.append((from_, m.group(1).upper()))
    imap.logout()
    return out


def main() -> None:
    rows = fetch_requests()
    if not rows:
        print("Новых запросов ключа не найдено.")
        return
    print(f"Найдено запросов: {len(rows)}\n")
    for from_, mid in rows:
        key = make_key(mid)
        print(f"От:    {from_}")
        print(f"ID:    {mid}")
        print(f"Ключ:  {key}")
        print(f"Ответ: {key} — вставьте ключ в окно активации.\n")


if __name__ == "__main__":
    main()
