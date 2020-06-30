from django import forms



class UrlForm(forms.Form):
    url = forms.URLField(label='', widget=forms.URLInput(attrs={'placeholder':'Enter url', 'class':' form-control form-control-lg'}))