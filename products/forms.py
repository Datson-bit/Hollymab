from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from products.models import Payment, Remark

PAYMENT_CHOICES=(
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

class CheckoutForm(forms.Form):
    street_address= forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'1234 Main st',
        'class':'form-control'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder':'Apartment or suite',
        'class':'form-control'
    }))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control'
    }))
    same_shipping_address = forms.BooleanField(required=False,widget=forms.CheckboxInput())
    save_info= forms.BooleanField(required=False, widget=forms.CheckboxInput())
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)




class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields= ('amount','email')


class RemarkForm(forms.ModelForm):
    class Meta:
        model= Remark
        fields = ('title', 'body')