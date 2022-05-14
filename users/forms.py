from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User, Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
 
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })
            
class CustomclearableProfile(forms.ClearableFileInput):
    template_name='users/custom_clearable_profile.html'

class ProfileUpdateForm(forms.ModelForm):
    picture = forms.ImageField(required=True, widget=CustomclearableProfile)
    class Meta:
        model = Profile 
        fields = ['picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })