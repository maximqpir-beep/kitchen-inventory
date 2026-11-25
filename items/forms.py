from django import forms
from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = (
            "name",
            "category",
            "condition",
            "room",
            "quantity",
            "unit_price",
            "image",
        )
        labels = {"unit_price": "Цена за штуку в копейках (100 = 1 руб.)"}
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Например, Кастрюля 5 л"}
            ),
            "quantity": forms.NumberInput(attrs={"min": 1}),
            "unit_price": forms.NumberInput(attrs={"min": 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["room"].disabled = True
            self.fields["room"].help_text = (
                "Для смены помещения оформите перемещение."
            )
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "content_type"):
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Фото должно быть не больше 5 МБ.")
            if image.image.format not in ("PNG", "JPEG", "WEBP"):
                raise forms.ValidationError("Допустимы PNG, JPEG и WEBP.")
            if image.image.width > 4096 or image.image.height > 4096:
                raise forms.ValidationError(
                    "Размер фото не больше 4096 × 4096."
                )
        return image
