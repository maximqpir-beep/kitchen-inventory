"""Подключение sqlite3, именованные строки и общие SQL-запросы."""

from contextlib import closing
from pathlib import Path
import re
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB = BASE_DIR / "data" / "inventory.sqlite"
DEFAULT_JSON = BASE_DIR / "data" / "inventory.json"
SCHEMA = BASE_DIR / "sql" / "schema.sql"
QUERIES_FILE = BASE_DIR / "sql" / "queries.sql"


class DataUnavailable(Exception):
    """База отсутствует, повреждена или имеет неверную структуру."""


def get_connection(path=DEFAULT_DB, *, readonly=False):
    """На каждом подключении включить FK и доступ row['name']."""
    path = Path(path).resolve()
    target = path.as_uri() + "?mode=ro" if readonly else str(path)
    conn = sqlite3.connect(target, uri=readonly, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def load_queries():
    """SQL хранится в одном файле; метки задают постоянные имена."""
    text = QUERIES_FILE.read_text(encoding="utf-8")
    chunks = re.split(r"^-- name: (\w+)\s*$", text, flags=re.M)
    return {chunks[i]: chunks[i + 1].strip()
            for i in range(1, len(chunks), 2)}


QUERIES = load_queries()


def fetch_all(name, parameters=(), *, path=DEFAULT_DB):
    """Имя выбирает разработчик, пользовательские значения идут в ?."""
    try:
        with closing(get_connection(path, readonly=True)) as conn:
            return conn.execute(QUERIES[name], parameters).fetchall()
    except (OSError, sqlite3.Error) as error:
        raise DataUnavailable("Не удалось прочитать SQLite.") from error


def fetch_one(name, parameters=(), *, path=DEFAULT_DB):
    rows = fetch_all(name, parameters, path=path)
    return rows[0] if rows else None
