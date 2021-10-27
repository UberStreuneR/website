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

class HowMuchCounterForm(forms.Form):
    counter = forms.IntegerField(label="",
                                 widget=forms.TextInput(attrs={'type': 'text',
                                                               'value': 0,
                                                               'id': 'counter',
                                                               'style': 'width: 40px;',
                                                               'class': 'text-center'}))
    # def __init__(self, id, *args, **kwargs):
    #     self.fields['counter'] = forms.IntegerField(label="",
    #                              widget=forms.TextInput(attrs={'type': 'text',
    #                                                            'value': 0,
    #                                                            'id': f'counter_{id}',
    #                                                            'style': 'width: 40px;',
    #                                                            'class': 'text-center'}))
    #     super(HowMuchCounterForm, self).__init__(*args, **kwargs)
    # Runtime generation of max value. Interesting.
    # also no necessity to pass class name and self into super() in python >=3.3