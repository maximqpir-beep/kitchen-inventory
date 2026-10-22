# Кухонный учет — ПР7

Система учета кухонного инвентаря. ЭФБО-12-24.
Предмет, категория, состояние, помещение и история перемещений.

## Запуск в Windows

Открой терминал в папке с `manage.py`. Нужен Python 3.10 или новее.

```bash
py -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
./.venv/Scripts/python.exe manage.py check
./.venv/Scripts/python.exe manage.py runserver
```

Открой http://127.0.0.1:8000/. Остановка сервера — Ctrl+C.
В проект уже включена база `data/inventory.sqlite`: 8 партий, 3 перемещения.
На Linux/macOS создай окружение через `python3 -m venv .venv`, затем
используй путь `./.venv/bin/python`.

## Что можно открыть

| Адрес | Назначение |
|---|---|
| `/` | Сводка и три самые дорогие партии |
| `/items/` | Поиск по названию, помещению, состоянию и категории |
| `/items/2/` | Карточка ножа: связанные данные получены через JOIN |
| `/items/available/` | Только исправный инвентарь, выбор помещения |
| `/rooms/` | Помещения и ссылки на их инвентарь |
| `/movements/` | Журнал с фильтрами даты, статуса и страницами по 20 записей |
| `/movements/1/` | Подробности перемещения |
| `/statistics/` | Количество, стоимость, категории, помещения, состояния |

Примеры: `/items/?q=НОЖ&room=3`, `/items/available/?room=1`,
`/movements/?date=2026-10-15&status=0`, `/statistics/?min_units=2`.
В журнале: `status=-1` — все записи, `0` — выполненные, `1` — отмененные.
На сайте пока доступны просмотр и поиск. Формы записи и Django ORM
добавляются в следующих практиках.

## SQLite и импорт

Сайт ПР7 читает **SQLite**, а консоль `main.py` по-прежнему работает с JSON.
Это два отдельных состояния: изменения консоли появятся на сайте после
явного повторного импорта. JSON и исходные классы ПР3 сохранены.

Для создания базы из JSON, если файл SQLite отсутствует:

```bash
./.venv/Scripts/python.exe -m db.import_json
```

Для **полной замены данных SQLite** содержимым JSON сначала сохрани копию
текущей базы, затем выполни:

```bash
./.venv/Scripts/python.exe -m db.import_json --replace
```

Обычный повторный импорт в заполненную базу отклоняется. `--replace`
заменяет записи одной транзакцией. Ошибки JSON и неуспешная вставка
не уничтожают прежние записи. Импорт не меняет исходный JSON.
Возможны отдельные пути: `--source data/inventory.json
--database data/inventory.sqlite`.

## Структура базы

Таблицы создаются в `sql/schema.sql`. Во всех таблицах `id INTEGER`
— первичный ключ. Прочие поля обязательные, кроме `rooms.description`.

| Таблица | Поля и типы |
|---|---|
| `categories` | `id INTEGER`, `name TEXT` |
| `conditions` | `id INTEGER`, `name TEXT`, `usable INTEGER` (0/1) |
| `rooms` | `id INTEGER`, `name TEXT`, `description TEXT` (допускает NULL) |
| `items` | `id INTEGER`, `name TEXT`, `name_search TEXT`, `category_id INTEGER`, `state_id INTEGER`, `room_id INTEGER`, `quantity INTEGER`, `unit_price INTEGER` |
| `movements` | `id INTEGER`, `item_id INTEGER`, `from_room INTEGER`, `to_room INTEGER`, `created_at TEXT`, `cancelled INTEGER` (0/1) |

Внешние ключи: `items.category_id → categories.id`, `items.state_id →
conditions.id`, `items.room_id → rooms.id`, `movements.item_id → items.id`,
`movements.from_room/to_room → rooms.id`. `PRAGMA foreign_keys = ON`
включается при каждом соединении. CHECK запрещает нулевое количество,
отрицательную цену, неверный статус и совпадение помещений перемещения.

Цена хранится целым числом копеек. Время — ISO-строкой.
`name_search` — название после Python `casefold()` для поиска кириллицы
без учета регистра; формируется импортом. Для ручного SQL-изменения имени
нужно также обновить это поле. Данные примера: 6 исправных предметов из 8,
стоимость 6 550.50 руб.; 2 выполненных и 1 отмененное перемещение.

## SQL и веб-слой

`db/database.py` подключает sqlite3, включает внешние ключи и
`conn.row_factory = sqlite3.Row`. `db/import_json.py` переносит данные
через `executemany()` и `commit()`. Django ORM не используется.

В `sql/queries.sql` 16 именованных запросов. Этот файл загружается самим
приложением: в Python нет второй копии запросов. Значения передаются
отдельным кортежем в `?`, пользовательский текст не вставляется в SQL.

| Запросы | Где виден результат |
|---|---|
| `rooms`, `categories`, `conditions` | Помещения и списки фильтров каталога |
| `items`, `available_items` | Каталог с WHERE и пригодный инвентарь |
| `item_detail`, `movements`, `movement_detail` | Карточки и журнал с JOIN |
| `inventory_totals`, `movement_totals`, `price_bounds` | Сводка, COUNT/SUM/MIN/MAX/AVG |
| `category_statistics`, `room_statistics`, `condition_statistics` | Группировка GROUP BY; LEFT JOIN сохраняет пустые группы |
| `heavy_rooms` | Фильтр групп HAVING по числу предметов |
| `expensive_items` | Три дорогие партии: ORDER BY, LIMIT, OFFSET |

`kitchen_site/source.py` передает результаты в views; views готовят context;
шаблоны отображают именованные поля строк. Предусмотрены пустые выборки,
400 при неверных параметрах, 404 при неизвестном ID и 503 при проблеме
с базой. GET/HEAD не меняют JSON или SQLite. Пример поиска по дате из
методички адаптирован в журнал перемещений: бронирований в этой теме нет.

## Проверка

```bash
./.venv/Scripts/python.exe manage.py check
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m flake8 . --extend-exclude=venv
./.venv/Scripts/python.exe -m db.verify_queries --cli
```

Последняя команда проверяет все 16 запросов и через Python API, и через
SQLite CLI. Для CLI нужен Python 3.12+ (`python -m sqlite3`) либо установленный
`sqlite3`. Обычная работа сайта совместима с Python 3.10+.
Для просмотра таблиц открой `data/inventory.sqlite` в SQLite Viewer.

Итог проверки ПР7: 104 теста прошли, `check` и flake8 без замечаний,
16 SQL-запросов проверены через API и CLI. Тесты работают с временной базой.
Проверены HTTP-ответы всех разделов и статических ресурсов.
Внешний вид и работа кнопки компактного вида требуют просмотра в браузере
на компьютере перед защитой.

## Материалы

Отчеты: `reports/PR5_REPORT.pdf`, `reports/PR6_REPORT.pdf`,
`reports/PR7_REPORT.pdf`. Рядом лежат редактируемые исходники `.md`.
В `DEFENSE.md` — короткое объяснение ПР7 и ответы на контрольные вопросы.
Папки `PR2/` и `PR3/` содержат отдельные ранее выполненные практики.
