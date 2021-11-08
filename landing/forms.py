from django import forms
from clients.models import Client
from .models import Order, File
class CheckoutForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ['name', 'phone', 'email']

class OrderDetailsForm(forms.ModelForm):
    details = forms.CharField(widget=forms.Textarea(
        {'style': 'width: 600px; height: 100px;',
         'placeholder': 'Ваши пожелания по заказу в свободной форме',
         'id': 'details'}
    ), label="Детали заказа")
    class Meta:
        model = Order
        fields = ['details']

class OrderFilesForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={
        'style': 'margin-top: 20px;',
        'multiple': 'multiple'
    }), label='')

