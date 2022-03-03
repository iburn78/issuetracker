from random import choice
from re import A
from django import forms
from board.models import Card, Post

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['title', 'image', 'card_color', 'desc', 'is_public', 'linked_card']
        widgets = {
            'is_public': forms.HiddenInput,  
            # 'card_color': forms.TextInput(attrs={'type': 'color'})
            'title': forms.TextInput(attrs={'class':'form-control',}), 
            'desc': forms.Textarea(attrs={'class':'form-control', 'rows':3}), 
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image1', 'image2', 'image3', 'tags', 'is_published']
        widgets = {
            'is_published': forms.HiddenInput
        }
