from django import forms
from board.models import Card, Post

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['title', 'image', 'card_color', 'desc', 'is_public', 'linked_card']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image1', 'image2', 'image3', 'tags', 'is_published']
