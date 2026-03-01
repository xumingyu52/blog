from django import forms
from .models import Title, Context, Comment

class TitleForm(forms.ModelForm):
    class Meta:
        model = Title
        fields = ['text']
        labels = {'text':''}

class ContextForm(forms.ModelForm):
    """context对应表单"""
    class Meta:
        model = Context
        fields = ['text','image']
        labels = {'text':'','image':''}

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'image']
        labels = {'text':''}