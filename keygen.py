"""CLI-генератор лицензионных ключей ФОТОН (только для владельца).

Использование:
    python keygen.py                      # случайные универсальные ключи
    python keygen.py --machine XXXX-XXXX  # ключ под конкретный Machine ID
    python keygen.py --universal          # печать 5 универсальных ключей
"""
from __future__ import annotations

import argparse
import sys

from photon.license import make_key, make_universal_key


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Генератор лицензионных ключей ФОТОН")
    p.add_argument("--machine", help="Machine ID из окна блокировки (XXXX-XXXX-XXXX)")
    p.add_argument("--count", type=int, default=1, help="сколько ключей (для универсальных)")
    args = p.parse_args()

    if args.machine:
        for _ in range(max(1, args.count)):
            print(make_key(args.machine))
    else:
        for i in range(max(1, args.count)):
            print(make_universal_key(f"photon-{i}"))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
