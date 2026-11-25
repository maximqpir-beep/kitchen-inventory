# Предыдущие практики

Эта папка хранит старый код. Текущий Django-сайт находится в ../apps/.

- main.py, inventory.py, models/ — консоль с обычными Python-классами.
- data/inventory.json — данные консоли.
- db/, sql/, data/inventory.sqlite — SQLite и SQL-запросы ПР7.
- snapshots/PR2/ и snapshots/PR3/ — отдельные версии прошлых практик.
- web_source_pr7.py — сохраненный слой чтения SQL предыдущего сайта.

Запуск консоли из корня проекта: `python legacy/main.py`.
Проверка SQL: перейди в legacy/ и выполни `python -m db.verify_queries --cli`.
Веб-сайт использует свою ORM-базу db.sqlite3; консоль ее не меняет.
