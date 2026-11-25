from django.contrib import admin
from movements.admin import MovementInline
from .models import Category, Condition, Item, Room


class ItemInline(admin.TabularInline):
    model = Item
    fields = ("name", "condition", "quantity", "unit_price")
    readonly_fields = fields
    extra = 0
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "usable")
    list_filter = ("usable",)
    search_fields = ("name",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "description")
    list_editable = ("name",)
    readonly_fields = ("slug",)
    inlines = (ItemInline,)
    list_per_page = 20
    view_on_site = True


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "condition",
        "room",
        "quantity",
        "total_price",
    )
    search_fields = ("name", "category__name", "room__name")
    list_filter = ("category", "condition", "room")
    list_select_related = ("category", "condition", "room")
    list_per_page = 20
    inlines = (MovementInline,)
    readonly_fields = ("total_price",)
    view_on_site = True

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        return fields + ("room",) if obj else fields
