"""Проверки настоящего числового меню и повторного запуска."""

import json
import os
from pathlib import Path
import subprocess
import sys

from utils import input_price

PROGRAM = Path(__file__).resolve().parents[1] / "main.py"


def run_cli(path: Path, commands: str) -> str:
    result = subprocess.run(
        [sys.executable, str(PROGRAM), "--data", str(path)],
        input=commands, capture_output=True, text=True, timeout=10,
        encoding="utf-8", check=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    assert not result.stderr
    return result.stdout


def test_move_persist_and_cancel(tmp_path):
    path = tmp_path / "inventory.json"
    output = run_cli(path, "5\n2\n3\n\n0\n")
    assert "Изменения сохранены" in output
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["items"][1]["room_id"] == 3
    output = run_cli(path, "9\n1\n\n0\n")
    assert "Изменения сохранены" in output
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["items"][1]["room_id"] == 1


def test_add_with_numeric_menu(tmp_path):
    path = tmp_path / "inventory.json"
    run_cli(path, "2\nЛожка\n4\n3\n25,50\n3\n1\n\n0\n")
    item = json.loads(path.read_text(encoding="utf-8"))["items"][-1]
    assert item["name"] == "Ложка"
    assert item["quantity"] == 3
    assert item["unit_price"] == 2550


def test_invalid_menu_then_exit(tmp_path):
    output = run_cli(tmp_path / "x.json", "abc\n99\n0\n")
    assert "Введите целое число" in output
    assert "Такого варианта нет" in output
    assert "Программа завершена" in output


def test_price_retries(monkeypatch):
    values = iter(["nan", "inf", "-1", "1.001", "abc", "12,50"])
    monkeypatch.setattr("builtins.input", lambda _: next(values))
    assert input_price() == 1250


def test_eof_cancels_unfinished_action(tmp_path):
    path = tmp_path / "inventory.json"
    output = run_cli(path, "2\nНовый\n")
    assert "Незавершенная операция не сохранена" in output
    assert len(json.loads(path.read_text(encoding="utf-8"))["items"]) == 8
