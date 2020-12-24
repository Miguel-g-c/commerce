from django import forms

class CreateForm(forms.Form):
    title = forms.CharField(max_length=25, label="Title")
    content = forms.CharField(widget=forms.Textarea, label="Content")
