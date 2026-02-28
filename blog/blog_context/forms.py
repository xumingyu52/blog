from django import forms
from .models import Title, Context

class TitleForm(forms.ModelForm):
    class Meta:
        model = Title
        fields = ['text']
        labels = {'text':''}

class ContextForm(forms.ModelForm):
    """context对应表单"""
    class Meta:
        model = Context
        fields = ['text']
        labels = {'text':''}

