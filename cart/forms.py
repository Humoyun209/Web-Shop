from django import forms
from django.utils.translation import gettext_lazy as _


class CartAddProductForm(forms.Form):
    PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES,
                                      coerce=int, label=_('Quantity'))
    override = forms.BooleanField(
        initial=False, required=False, widget=forms.HiddenInput
    )
