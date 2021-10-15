from django import forms

class ExcelItemsForm(forms.Form):
    file = forms.FileField()