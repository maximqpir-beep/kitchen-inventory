"""Копирование SQLite ПР7 в отдельную базу ORM без изменения исходника."""

from contextlib import closing
from datetime import datetime
from pathlib import Path
import sqlite3

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from items.models import Category, Condition, Item, Room
from movements.models import Movement


class Command(BaseCommand):
    help = "Перенести SQLite ПР7 в пустую ORM-базу, сохранив ID и связи."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source", type=Path, default=settings.DATABASE_PATH
        )

    def handle(self, *args, **options):
        source = options["source"].resolve()
        if source == Path(settings.DATABASES["default"]["NAME"]).resolve():
            raise CommandError("Исходная и целевая базы должны различаться.")
        try:
            with closing(
                sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
            ) as conn:
                conn.row_factory = sqlite3.Row
                data = {
                    table: [
                        dict(x) for x in conn.execute("SELECT * FROM " + table)
                    ]
                    for table in (
                        "categories",
                        "conditions",
                        "rooms",
                        "items",
                        "movements",
                    )
                }
                if conn.execute("PRAGMA foreign_key_check").fetchall():
                    raise ValueError("Нарушены внешние ключи в исходнике.")
            with transaction.atomic():
                if any(
                    model.objects.exists()
                    for model in (Category, Condition, Room, Item, Movement)
                ):
                    raise CommandError(
                        "Целевая база не пуста; импорт отменен."
                    )
                for model, table in (
                    (Category, "categories"),
                    (Condition, "conditions"),
                    (Room, "rooms"),
                ):
                    for raw in data[table]:
                        model.objects.create(
                            pk=raw["id"],
                            name=raw["name"],
                            **(
                                {"usable": bool(raw["usable"])}
                                if model is Condition
                                else (
                                    {"description": raw["description"] or ""}
                                    if model is Room
                                    else {}
                                )
                            ),
                        )
                for raw in data["items"]:
                    item = Item(
                        pk=raw["id"],
                        name=raw["name"],
                        category_id=raw["category_id"],
                        condition_id=raw["state_id"],
                        room_id=raw["room_id"],
                        quantity=raw["quantity"],
                        unit_price=raw["unit_price"],
                    )
                    item.name_search = item.name.casefold()
                    item.full_clean()
                    item.save()
                for raw in data["movements"]:
                    created = datetime.fromisoformat(raw["created_at"])
                    if timezone.is_naive(created):
                        created = timezone.make_aware(created)
                    Movement.objects.create(
                        pk=raw["id"],
                        item_id=raw["item_id"],
                        source_id=raw["from_room"],
                        target_id=raw["to_room"],
                        created_at=created,
                        cancelled=bool(raw["cancelled"]),
                    )
        except (sqlite3.Error, ValueError, KeyError) as error:
            raise CommandError(str(error)) from error
        self.stdout.write(
            self.style.SUCCESS(
                f"Импорт: {len(data['items'])} партий, "
                f"{len(data['movements'])} перемещений. Исходник сохранен."
            )
        )
