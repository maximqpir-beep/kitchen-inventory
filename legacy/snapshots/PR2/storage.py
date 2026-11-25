"""Загрузка и безопасная запись JSON без зависимости от текущей папки."""

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from catalog import demo_data
from inventory import export_data, import_data

DEFAULT_PATH = Path(__file__).resolve().parent / "data" / "inventory.json"


def load_data(path: Path = DEFAULT_PATH) -> dict:
    """При отсутствии файла создать набор; поврежденный файл не менять."""
    if not path.exists():
        data = import_data(demo_data())
        save_data(data, path)
        return data
    with path.open(encoding="utf-8") as stream:
        raw = json.load(stream)
    return import_data(raw)


def save_data(data: dict, path: Path = DEFAULT_PATH) -> None:
    """Записать временный файл, затем атомарно заменить целевой."""
    raw = export_data(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=path.name, suffix=".tmp", delete=False,
        ) as stream:
            temp_path = Path(stream.name)
            json.dump(raw, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
