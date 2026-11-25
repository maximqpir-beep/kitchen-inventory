from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Movement
from .services import cancel_movement, complete_movement, save_plan


class MovementAdminForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ("item", "target", "scheduled_for", "note")

    def clean(self):
        cleaned = super().clean()
        item = cleaned.get("item")
        if item:
            self.instance.source_id = item.room_id
        return cleaned


class MovementInline(admin.TabularInline):
    model = Movement
    fk_name = "item"
    fields = ("source", "target", "scheduled_for", "status")
    readonly_fields = fields
    extra = 0
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    form = MovementAdminForm
    list_display = (
        "id",
        "item",
        "source",
        "target",
        "scheduled_for",
        "status",
    )
    search_fields = ("item__name", "source__name", "target__name")
    list_filter = ("status", "scheduled_for", "source", "target")
    date_hierarchy = "scheduled_for"
    list_select_related = ("item", "source", "target")
    ordering = ("-scheduled_for", "-pk")
    list_per_page = 20
    actions = ("complete_selected", "cancel_selected")
    readonly_fields = ("source", "status", "created_at", "executed_at")
    view_on_site = True

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj and obj.status != Movement.Status.PLANNED:
            return fields + ("item", "target", "scheduled_for")
        return fields

    def save_model(self, request, obj, form, change):
        if change and obj.status != Movement.Status.PLANNED:
            obj.save(update_fields=["note"])
        else:
            save_plan(obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def apply(self, request, queryset, operation):
        success = 0
        for pk in queryset.values_list("pk", flat=True):
            try:
                operation(pk)
                success += 1
            except ValidationError as error:
                self.message_user(
                    request, "; ".join(error.messages), level=messages.WARNING
                )
        self.message_user(request, f"Изменено записей: {success}.")

    @admin.action(
        description="Выполнить выбранные перемещения", permissions=["change"]
    )
    def complete_selected(self, request, queryset):
        self.apply(request, queryset, complete_movement)

    @admin.action(
        description="Отменить выбранные перемещения", permissions=["change"]
    )
    def cancel_selected(self, request, queryset):
        self.apply(request, queryset, cancel_movement)
