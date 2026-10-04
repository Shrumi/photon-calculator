"""Каталог услуг фото-салона «ФОТОН» + умный поиск по 2 буквам.

Раскладка: латиница → кириллица (ЙЦУКЕН), регистр не важен.
"""
from __future__ import annotations

from dataclasses import dataclass

LAYOUT = str.maketrans(
    "qwertyuiop[]asdfghjkl;'zxcvbnm,.`"
    "QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>~",
    "йцукенгшщзхъфывапролджэячсмитьбюё"
    "ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ",
)


@dataclass(frozen=True)
class Service:
    code: str
    name: str
    category: str
    price: float


SERVICES: list[Service] = [
    Service("print10", "Печать фото 10×15", "Печать", 15.0),
    Service("print13", "Печать фото 13×18", "Печать", 35.0),
    Service("print15", "Печать фото 15×21", "Печать", 55.0),
    Service("print20", "Печать фото 20×30", "Печать", 95.0),
    Service("lamA4", "Ламинация A4", "Печать", 60.0),
    Service("lamA5", "Ламинация A5", "Печать", 40.0),
    Service("scan", "Сканирование", "Печать", 20.0),
    Service("copy", "Копирование", "Печать", 10.0),
    Service("mug", "Кружка с фото", "Сувенирка", 350.0),
    Service("tshirt", "Футболка с фото", "Сувенирка", 850.0),
    Service("magnet", "Магнит с фото", "Сувенирка", 120.0),
    Service("puzzle", "Пазл с фото", "Сувенирка", 650.0),
    Service("book20", "Фотокнига 20×20", "Фотокниги", 1900.0),
    Service("book25", "Фотокнига 25×25", "Фотокниги", 2900.0),
    Service("rest", "Реставрация фото", "Услуги", 500.0),
    Service("retouch", "Ретушь фото", "Услуги", 300.0),
    Service("passport", "Фото на документы", "Услуги", 250.0),
    Service("visa", "Фото на визу", "Услуги", 400.0),
]


def _normalize(q: str) -> str:
    return q.strip().lower().translate(LAYOUT)


def search_services(q: str) -> list[dict]:
    """Поиск по первым буквам названия (2+ достаточно), раскладка/регистр любые."""
    nq = _normalize(q)
    if not nq:
        return []
    out = []
    for s in SERVICES:
        name = s.name.lower()
        if name.startswith(nq) or any(w.startswith(nq) for w in name.split()):
            out.append({"code": s.code, "name": s.name, "category": s.category, "price": s.price})
    if not out:  # мягкий фолбэк: подстрока
        out = [
            {"code": s.code, "name": s.name, "category": s.category, "price": s.price}
            for s in SERVICES
            if nq in s.name.lower()
        ]
    return out[:8]
