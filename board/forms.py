from email.policy import default
from random import choice
from re import A
import re
from django import forms
from board.models import Card, Post

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['title', 'image', 'card_color', 'desc', 'is_public', 'linked_card']
        widgets = {
            # 'is_public': forms.HiddenInput,  
            'is_public': forms.CheckboxInput,  
            # 'card_color': forms.TextInput(attrs={'type': 'color'})
            'title': forms.TextInput(attrs={'class':'form-control',}), 
            'desc': forms.Textarea(attrs={'class':'form-control', 'rows':3}), 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({
            'class': 'form-control',
        })

class Customclearable(forms.ClearableFileInput):
    template_name='board/custom_clearable_file.html'

class PostForm(forms.ModelForm):
    image1_input = forms.ImageField(required=False, widget=Customclearable)
    image2_input = forms.ImageField(required=False, widget=Customclearable)
    image3_input = forms.ImageField(required=False, widget=Customclearable)
    image4_input = forms.ImageField(required=False, widget=Customclearable)
    image5_input = forms.ImageField(required=False, widget=Customclearable)
    image6_input = forms.ImageField(required=False, widget=Customclearable)
    image7_input = forms.ImageField(required=False, widget=Customclearable)
    class Meta:
        model = Post
        fields = ['content', 'tags', 'is_published', 'image1_input', 'image2_input', 'image3_input', 'image4_input', 'image5_input', 'image6_input', 'image7_input']
        widgets = {
            'content': forms.Textarea(attrs={'rows':'4',}), 
            'is_published': forms.HiddenInput,
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })
