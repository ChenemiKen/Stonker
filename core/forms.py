from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget



PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 26)]

class CartAddForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)
    

PAYMENT_OPTIONS = (
    ('stripe', 'Stripe'),
    ('paypal', "Paypal")
) 
class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'1234 Main St'}))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder':'Apartment or suite'}))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={'class': 'custom-select d-block w-100'}))
    zip = forms. CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    same_shipping_address = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    save_info = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_OPTIONS)

