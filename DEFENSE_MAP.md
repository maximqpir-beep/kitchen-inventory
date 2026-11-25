# Что открыть преподавателю

Тема: система учета кухонного инвентаря. Группа ЭФБО-12-24.
**Рабочий сайт находится в apps/. Начинай показ с этой папки.**

## ПР9 — модели и ORM

| Преподаватель просит | Открой | Что показать |
|---|---|---|
| Модели предмета и справочников | [apps/items/models.py](apps/items/models.py) | Category, Condition, Room, Item; поля и ForeignKey |
| Модель перемещения | [apps/movements/models.py](apps/movements/models.py) | Movement, ссылки на предмет и помещения, constraints |
| Миграции | apps/items/migrations/ и apps/movements/migrations/ | 0001 — создание; 0002 — развитие и перенос статусов |
| Перенос старых данных | [apps/items/management/commands/import_legacy.py](apps/items/management/commands/import_legacy.py) | readonly-источник, transaction.atomic, сохранение ID |
| ORM-запросы | [config/orm.py](config/orm.py) | aggregate, annotate, F, select_related, Paginator |
| Поиск и фильтры каталога | [apps/items/views.py](apps/items/views.py) | item_list, available, item_detail |
| Примеры 15 запросов | [docs/ORM_QUERIES.md](docs/ORM_QUERIES.md) | Перечень выражений и назначение |

## ПР10 — Admin и оптимизация

| Преподаватель просит | Открой | Что показать |
|---|---|---|
| Настройки админки | [apps/items/admin.py](apps/items/admin.py) | list_display, search_fields, list_filter, inline |
| Админку перемещений | [apps/movements/admin.py](apps/movements/admin.py) | Столбцы, фильтры, безопасные действия |
| Статусы и свой QuerySet | [apps/movements/models.py](apps/movements/models.py) | TextChoices, active/completed/cancelled/for_date |
| Преобразование старых статусов | apps/movements/migrations/0002_*.py | RunPython до RemoveField |
| GeneratedField и slug | [apps/items/models.py](apps/items/models.py) | Item.total_price; Room.slug, save, get_absolute_url |
| Контекстный процессор | [config/context_processors.py](config/context_processors.py) | Общие название сайта и группа |
| Debug Toolbar | [config/settings.py](config/settings.py) | Условное подключение; на сайте открыть SQL-панель |
| Проверки N+1 | [tests/test_orm.py](tests/test_orm.py) | test_no_n_plus_one |

## ПР11 — формы и действия

| Преподаватель просит | Открой | Что показать |
|---|---|---|
| Форму фильтрации | [apps/movements/forms.py](apps/movements/forms.py) | MovementFilterForm (forms.Form) |
| Форму создания/редактирования | [apps/movements/forms.py](apps/movements/forms.py) | MovementForm (ModelForm), Meta, clean |
| Проверку GET, обработку POST | [apps/movements/views.py](apps/movements/views.py) | movement_list, edit_form, create, edit |
| Правила предметной области | [apps/movements/services.py](apps/movements/services.py) | save_plan, complete_movement, cancel_movement |
| CSRF и вывод ошибок | [apps/movements/templates/movements/movement_form.html](apps/movements/templates/movements/movement_form.html) | csrf_token и includes/form_fields.html |
| Поля и ошибки формы | [templates/includes/form_fields.html](templates/includes/form_fields.html) | field.errors, non_field_errors |
| Загрузку фото | [apps/items/forms.py](apps/items/forms.py) | ItemForm.clean_image; затем items/views.py и item_form.html |
| Права доступа | [apps/movements/views.py](apps/movements/views.py) | login_required, permission_required, require_POST |
| Тесты форм и CSRF | [tests/test_forms.py](tests/test_forms.py) | Дата, конфликт, редактирование, отмена, права и фото |

## Шаблоны, адреса, оформление

- Общие адреса: config/urls.py. Адреса приложений: apps/<приложение>/urls.py.
- Общий каркас: templates/base.html. Навигация и пагинация: templates/includes/.
- Страницы каталога и форм предметов: apps/items/templates/items/.
- Страницы перемещений: apps/movements/templates/movements/.
- Главная и статистика: apps/homepage/views.py и templates/homepage/ внутри приложения.
- CSS, JavaScript и картинки: apps/homepage/static/homepage/.
- Отчеты: reports/PR9/, reports/PR10/, reports/PR11/.
- Скриншоты: reports/PR10/screenshots/ и reports/PR11/screenshots/.

## Что лежит в legacy/

Это предыдущие реализации, **не основной код ПР9–ПР11**:
консоль main.py, обычные Python-классы models/, JSON, SQL ПР7, отдельные версии ПР2/ПР3.
Текущие модели Django — apps/items/models.py и apps/movements/models.py.
Короткие пояснения для устного ответа: docs/DEFENSE.md.

## Команды перед показом

```bash
./.venv/Scripts/python.exe manage.py check
./.venv/Scripts/python.exe manage.py showmigrations
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe manage.py runserver
```
