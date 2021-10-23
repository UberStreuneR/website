from django import forms


class ExcelItemsForm(forms.Form):
    file = forms.FileField()

class SearchForm(forms.Form):
    text = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'id': 'article',
                   'aria-label': 'Sizing example input',
                   'aria-describedby': 'inputGroup-sizing-sm',
                   # 'placeholder': 'name@example.com',
                   'type': 'text'}
        )
    )