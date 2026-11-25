"""Безопасная демонстрация create/save/get/delete с откатом транзакции."""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.items.models import Room


class Command(BaseCommand):
    help = "Показать ORM CRUD на временном помещении без сохранения изменений."

    @transaction.atomic
    def handle(self, *args, **options):
        room = Room.objects.create(name="Временное помещение для защиты")
        room.description = "Изменено через save()"
        room.save(update_fields=["description"])
        self.stdout.write(Room.objects.get(pk=room.pk).description)
        room.delete()
        transaction.set_rollback(True)
        self.stdout.write("create/save/get/delete: OK; транзакция отменена.")
