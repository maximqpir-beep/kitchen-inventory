"""Проверка всех запросов: python -m db.verify_queries --cli."""

import argparse
from contextlib import closing
from pathlib import Path
import shutil
import subprocess
import sys

from db.database import DEFAULT_DB, QUERIES, get_connection

EXAMPLES = {
    "rooms": (), "categories": (), "conditions": (),
    "items": ("%нож%", 0, 0, 0, 0, 0, 0),
    "available_items": (0, 0), "item_detail": (1,),
    "movements": ("", "", -1, -1, 20, 0), "movement_detail": (1,),
    "inventory_totals": (), "movement_totals": (), "price_bounds": (),
    "category_statistics": (), "room_statistics": (),
    "condition_statistics": (), "heavy_rooms": (2,),
    "expensive_items": (3, 0),
}


def verify(database=DEFAULT_DB, *, cli=False):
    """Один файл SQL проверяется через API и, по запросу, через CLI."""
    sqlite_cli = shutil.which("sqlite3")
    if cli and not sqlite_cli and sys.version_info < (3, 12):
        raise RuntimeError("Для CLI нужен sqlite3 или Python 3.12+.")
    with closing(get_connection(database, readonly=True)) as conn:
        for name, sql in QUERIES.items():
            rendered = []
            conn.set_trace_callback(rendered.append)
            result = conn.execute(sql, EXAMPLES[name]).fetchall()
            conn.set_trace_callback(None)
            if cli:
                # SQLite сам связал параметры. Пользовательский ввод не
                # интерполируется; shell не используется.
                command = ([sqlite_cli] if sqlite_cli else
                           [sys.executable, "-m", "sqlite3"])
                command += [str(Path(database).resolve()), rendered[-1]]
                subprocess.run(command, check=True, capture_output=True,
                               text=True)
            print(f"{name}: OK, строк {len(result)}")
    print(f"Проверено запросов: {len(QUERIES)}. "
          f"CLI: {'да' if cli else 'нет'}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--cli", action="store_true")
    args = parser.parse_args()
    verify(args.database, cli=args.cli)
