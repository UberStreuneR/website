from django import forms
from clients.models import Client

class CheckoutForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = ['name', 'phone', 'email']