from email.policy import default
from random import choice
from django import forms
from .models import Card, Post, Comment
COMMENT_MAX_LENGTH = '1000'

class Customclearable(forms.ClearableFileInput):
    template_name='board/custom_clearable_file.html'

class Cardclearable(forms.ClearableFileInput):
    template_name='board/card_clearable_file.html'

class CardForm(forms.ModelForm):
    image_input = forms.ImageField(required=False, widget=Cardclearable)
    default_img = forms.CharField(required=False)
    toggle_official = forms.BooleanField(required=False)
    class Meta:
        model = Card
        fields = ['title', 'image_input', 'default_img', 'card_color', 'desc', 'is_public', 'is_official', 'toggle_official', 'is_geocard']
        widgets = {
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input', }),
            'is_official': forms.CheckboxInput(attrs={'class': 'form-check-input', }),
            'is_geocard': forms.CheckboxInput(attrs={'class': 'form-check-input', }),
            'toggle_official': forms.CheckboxInput(attrs={'class': 'form-check-input', }),
            'title': forms.TextInput(attrs={'spellcheck': 'true', 'class':'form-control',}), 
            'desc': forms.Textarea(attrs={'spellcheck': 'true', 'class':'form-control', 'rows':3}), 
            'default_img': forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image_input'].widget.attrs.update({
            'class': 'form-control',
        })

class PostForm(forms.ModelForm):
    image1_input = forms.ImageField(required=False, widget=Customclearable)
    image2_input = forms.ImageField(required=False, widget=Customclearable)
    image3_input = forms.ImageField(required=False, widget=Customclearable)
    image4_input = forms.ImageField(required=False, widget=Customclearable)
    image5_input = forms.ImageField(required=False, widget=Customclearable)
    image6_input = forms.ImageField(required=False, widget=Customclearable)
    image7_input = forms.ImageField(required=False, widget=Customclearable)
    mimages = forms.ImageField(required=False, widget=Customclearable(attrs={'multiple': True}))
    mimage_keys = forms.CharField(required=False)

    class Meta:
        model = Post
        fields = ['title', 'content', 'tags', 'mimages', 'mimage_keys', 'is_html', 'image1_input', 'image2_input', 'image3_input', 'image4_input', 'image5_input', 'image6_input', 'image7_input']
        widgets = {
            'title': forms.TextInput(attrs={'spellcheck': 'true'}), 
            'content': forms.Textarea(attrs={'spellcheck': 'true', 'rows':'12', 'placeholder':''}), 
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })
            if field == "tags":
                self.fields[field].widget.attrs.update({
                    'autocorrect':'off', 'autocapitalize':'off',
                })

class CommentForm(forms.ModelForm):

    class Meta: 
        model = Comment
        fields = ['content',]
        labels = {
            'content': 'comment', 
        }
        widgets = {
            'content': forms.Textarea(attrs={'spellcheck': 'true', 'rows':'2', 'placeholder':'', 'maxlength':COMMENT_MAX_LENGTH,}), 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })