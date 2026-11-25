"""Запуск: python -m db.import_json; повторный импорт: --replace."""

import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3

from catalog import CATEGORIES, ROOMS, STATES
from db.database import DEFAULT_DB, DEFAULT_JSON, SCHEMA, get_connection
from validation import check_data


def import_json(source=DEFAULT_JSON, database=DEFAULT_DB, *, replace=False):
    """Проверить исходник и атомарно импортировать, сохранив ID и связи."""
    raw = json.loads(Path(source).read_text(encoding="utf-8"))
    check_data(raw)
    database = Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)
    with closing(get_connection(database)) as conn:
        conn.executescript(SCHEMA.read_text(encoding="utf-8"))
        count = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        if count and not replace:
            raise ValueError(
                "База уже содержит предметы. Для замены нужен --replace."
            )
        try:
            conn.execute("BEGIN IMMEDIATE")
            for table in ("movements", "items", "rooms", "conditions",
                          "categories"):
                # Имена только из постоянного кортежа, не из ввода.
                conn.execute("DELETE FROM " + table)
            conn.executemany(
                "INSERT INTO categories(id, name) VALUES (?, ?)",
                CATEGORIES.items(),
            )
            conn.executemany(
                "INSERT INTO conditions(id, name, usable) VALUES (?, ?, ?)",
                [(key, name, int(key == 1))
                 for key, name in STATES.items()],
            )
            conn.executemany(
                "INSERT INTO rooms(id, name, description) VALUES (?, ?, ?)",
                [(key, name, None) for key, name in ROOMS.items()],
            )
            conn.executemany(
                "INSERT INTO items(id, name, name_search, category_id, "
                "state_id, room_id, quantity, unit_price) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [(item["id"], item["name"].strip(),
                  item["name"].strip().casefold(), item["category_id"],
                  item["state_id"], item["room_id"], item["quantity"],
                  item["unit_price"]) for item in raw["items"]],
            )
            conn.executemany(
                "INSERT INTO movements(id, item_id, from_room, to_room, "
                "created_at, cancelled) VALUES (?, ?, ?, ?, ?, ?)",
                [(move["id"], move["item_id"], move["from_room"],
                  move["to_room"], move["created_at"],
                  int(move["cancelled"])) for move in raw["moves"]],
            )
            conn.commit()
        except (sqlite3.Error, OverflowError):
            conn.rollback()
            raise
    return {"items": len(raw["items"]), "movements": len(raw["moves"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--database", type=Path, default=DEFAULT_DB)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    try:
        result = import_json(args.source, args.database,
                             replace=args.replace)
    except (OSError, ValueError, sqlite3.Error, OverflowError) as error:
        parser.exit(1, f"Импорт не выполнен: {error}\n")
    print(f"Импортировано партий: {result['items']}; "
          f"перемещений: {result['movements']}.")


if __name__ == "__main__":
    main()
