"""GET-фильтры и ModelForm с явным перечнем разрешенных полей."""

from django import forms
from django.utils import timezone

from apps.items.models import Item, Room
from .models import Movement


class MovementFilterForm(forms.Form):
    date = forms.DateField(
        label="Дата перемещения",
        required=False,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    status = forms.ChoiceField(
        label="Статус",
        required=False,
        choices=[
            ("all", "Все записи"),
            *Movement.Status.choices,
        ],
    )
    room = forms.ModelChoiceField(
        label="Помещение маршрута",
        required=False,
        queryset=Room.objects.all(),
        empty_label="Все помещения",
    )
    item = forms.ModelChoiceField(
        label="Предмет",
        required=False,
        queryset=Item.objects.all(),
        empty_label="Все предметы",
    )
    q = forms.CharField(
        label="Поиск по предмету или назначению",
        required=False,
        max_length=200,
    )
    sort = forms.ChoiceField(
        label="Порядок",
        required=False,
        choices=[
            ("newest", "Новые первыми"),
            ("oldest", "Старые первыми"),
            ("item", "По предмету"),
        ],
    )
    page = forms.IntegerField(
        required=False, min_value=1, widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class MovementForm(forms.ModelForm):
    scheduled_for = forms.DateField(
        label="Дата перемещения",
        initial=timezone.localdate,
        input_formats=["%Y-%m-%d"],
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )

    class Meta:
        model = Movement
        fields = ("item", "target", "scheduled_for", "note")
        labels = {"target": "Помещение назначения"}
        widgets = {
            "note": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Необязательное примечание"}
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = Item.objects.with_related()
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_scheduled_for(self):
        value = self.cleaned_data["scheduled_for"]
        if value < timezone.localdate():
            raise forms.ValidationError(
                "Нельзя планировать на прошедшую дату."
            )
        return value

    def clean(self):
        cleaned = super().clean()
        item = cleaned.get("item")
        if item:
            self.instance.source_id = item.room_id
        return cleaned
