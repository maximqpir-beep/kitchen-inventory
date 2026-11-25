# ORM-запросы ПР9 (используются в приложении)

| № | Выражение / место | Назначение |
|---|---|---|
| 1 | `Room.objects.all()` | Список помещений |
| 2 | `get_object_or_404(orm.item_list(), pk=...)` | Один предмет |
| 3 | `items.filter(room_id=...)` | Одно условие |
| 4 | `items.filter(room_id=..., condition__usable=True)` | Несколько условий |
| 5 | `Item.objects.usable()` | Поле связанной модели |
| 6 | `items.exclude(condition__usable=False)` | Исключение непригодных |
| 7 | `Q(name_search__contains=...)` | Поиск названия без регистра кириллицы |
| 8 | `Q(name_search__contains=...) \| Q(category__name_search__contains=...)` | Поиск в названии и категории |
| 9 | `items.order_by('name_search', 'pk')` | Устойчивая сортировка |
| 10 | `items.order_by('room__name', 'pk')` | Сортировка по связанному объекту |
| 11 | `select_related('category', 'condition', 'room')` | Каталог без N+1 |
| 12 | `select_related('item', 'source', 'target')` | Связи перемещений |
| 13 | `Item.objects.aggregate(...)` | COUNT, SUM, условная сумма |
| 14 | `Item.objects.aggregate(Min, Max, Avg)` | Показатели цен |
| 15 | `Category.objects.values('id', 'name').annotate(...)` | Группы по категориям |
| 16 | `Room.objects.values(...).annotate(...).filter(units__gte=...)` | Группировка и HAVING |
| 17 | `Movement.objects.filter(created_at__date=...)` | Дата перемещения |
| 18 | `Movement.objects.filter(cancelled=...)` | Статус истории в ПР9 |
| 19 | `Paginator(queryset, 20).get_page(...)` | Постраничный вывод |
| 20 | `with_cost().order_by('-cost', 'pk')[:3]` | F-выражение, дорогие партии |
| 21 | `Room.objects.create(...)`, `save()`, `delete()` | CRUD в команде orm_demo с откатом |

В ПР10 отбор по cancelled заменяется на методы QuerySet active/cancelled/completed;
в ПР11 условия из GET проходят через Django Forms. Прямой SQL ПР7 сохранен
в db/ и sql/ для отдельной демонстрации, веб-представления его не вызывают.
