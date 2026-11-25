# Кухонный учет — ЭФБО-12-24

## Первый запуск (Windows / Git Bash)

Открой терминал в папке с manage.py. Нужен Python 3.10+.

```bash
py -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
./.venv/Scripts/python.exe manage.py migrate
./.venv/Scripts/python.exe manage.py import_legacy
./.venv/Scripts/python.exe manage.py createsuperuser
./.venv/Scripts/python.exe manage.py runserver
```

Открой http://127.0.0.1:8000/. На Linux/macOS используй `python3` и `.venv/bin/python`.
Импорт нужен один раз в пустую базу. Если база заполнена, команда безопасно откажет.
При обновлении существующего проекта сохрани копию db.sqlite3 и выполни migrate.
Для обычного следующего запуска достаточно `manage.py runserver`.

## Папки

| Где | Что находится |
|---|---|
| apps/items/ | Модели предметов и справочников, формы, каталог, Admin |
| apps/movements/ | Модель перемещения, формы, выполнение и отмена, Admin |
| apps/homepage/ | Главная, помещения, статистика, CSS/JS/изображения |
| config/ | Настройки Django, корневые URL и общие ORM-запросы |
| templates/ | Общие шаблоны, навигация, поля форм, ошибки |
| tests/ | Тесты ORM, Admin, форм и сайта |
| docs/ | Подробное руководство, ORM-запросы, объяснения для защиты |
| reports/PR9/, PR10/, PR11/ | Отчет каждой практики и ее скриншоты |
| legacy/ | Старая консоль, JSON, SQL ПР7 и отдельные версии ПР2/ПР3 |

Текущая рабочая база — db.sqlite3 (создается migrate, в Git не хранится).
Исходник ПР7 для импорта — legacy/data/inventory.sqlite. Фото сохраняются в media/.
Перенос папок не меняет метки моделей, таблицы базы или адреса страниц сайта.

## Проверка

```bash
./.venv/Scripts/python.exe manage.py check
./.venv/Scripts/python.exe manage.py makemigrations --check --dry-run
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m flake8 . --extend-exclude=venv
```

После переупорядочивания прошли все 97 тестов, новых миграций не требуется.
Подробнее о правилах перемещений и возможностях: [docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md).
