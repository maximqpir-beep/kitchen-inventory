# Кухонный учет — ПР9

Система учета кухонного инвентаря. ЭФБО-12-24.
Предмет, категория, состояние, помещение и история перемещений.

## Запуск (Windows / Git Bash)

```bash
py -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
./.venv/Scripts/python.exe manage.py migrate
./.venv/Scripts/python.exe manage.py import_legacy
./.venv/Scripts/python.exe manage.py runserver
```

Открой http://127.0.0.1:8000/. Для Linux/macOS: `python3 -m venv .venv`,
путь к Python: `./.venv/bin/python`.
`import_legacy` выполняется **один раз** в пустую ORM-базу. Повторный запуск
отклоняется, данные не перезаписываются. При обычном следующем запуске нужны
только migrate (если есть новые миграции) и runserver.

ПР9: модели `Category`, `Condition`, `Room`, `Item` в items/models.py и
`Movement` в movements/models.py, связи PROTECT и related_name, миграции.
Новая рабочая база `db.sqlite3` создается migrate и исключена из Git.
Исходная `data/inventory.sqlite` из ПР7 не изменяется; ID и связи сохраняются.
JSON и консоль main.py сохранены как предыдущая независимая реализация.
Веб-страницы теперь используют только ORM.

Страницы: `/`, `/items/`, `/items/2/`, `/items/available/`, `/rooms/`,
`/movements/`, `/movements/1/`, `/statistics/`. В каталоге работают поиск
по названию и категории, фильтры и сортировка; в журнале — дата, статус,
поиск, сортировка, Paginator. Переходы сохраняют параметры.
Сводки вычисляются aggregate/annotate; пустые помещения остаются в статистике.

Примеры минимум 15 ORM-выражений: `docs/ORM_QUERIES.md`.
Безопасная демонстрация CRUD с откатом: `python manage.py orm_demo`.

Проверка:
```bash
./.venv/Scripts/python.exe manage.py check
./.venv/Scripts/python.exe manage.py showmigrations
./.venv/Scripts/python.exe manage.py makemigrations --check --dry-run
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m flake8 . --extend-exclude=venv
```
Проверены 68 тестов: прежняя предметная логика, перенос данных, ORM,
ограничения, страницы, параметры, поиск, экранирование, пагинация и N+1.
