from logging import exception
from django.shortcuts import render, redirect
# use info, success, warning to make it consistent with bootstrap5
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.core.mail import send_mail
import datetime
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from users.models import User, DEFAULT_PIC
from PIL import Image, ImageOps
from io import BytesIO
from board.tools import image_resize, exception_log
from django.core.files.base import ContentFile
import os
PROFILE_PIC_MAXSIZE = 2000


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'account created for {username}!')
            send_mail(
                f'New User ({username}) to issuetracker.info has been added.',
                f'''{username} is registred at {datetime.datetime.now()}''',
                'issuetree.tracker@gmail.com',
                ['issuetree.tracker@gmail.com'],
                fail_silently=False,
            )
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile, initial={'picture': request.user.profile.image})
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            file_to_delete = str(p_form.instance.image)
            try:
                if os.path.basename(file_to_delete) != DEFAULT_PIC:
                    p_form.instance.image.delete()
            except: 
                text = "Exception in delete profile pic - view fuction profile(): " + file_to_delete
                exception_log(text)

            with Image.open(p_form.cleaned_data['picture']) as img:
                img_io = BytesIO()
                ft = img.format
                img = image_resize(PROFILE_PIC_MAXSIZE, img)
                res = ImageOps.exif_transpose(img)
                res.save(img_io, format=ft)
                p_form.instance.image.save(os.path.basename(p_form.cleaned_data['picture'].name), ContentFile(img_io.getvalue()))
                res.close()
            p_form.save()
            messages.success(request, 'your account has been updated')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile, initial={'picture': request.user.profile.image})

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)


class MyLoginView(LoginView):
    template_name='users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get_redirect_url(self):
        next = self.request.GET.get('next', 'none')
        if 'login' in next or 'register' in next:
            return '/'
        return super().get_redirect_url()

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MyLogoutView(LogoutView):
    def setup(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return super().setup(request, *args, **kwargs)
        else:
            return redirect('mainr')

    def get(self, request, *args, **kwargs):
        messages.success(self.request, "you have been logged-out")
        return redirect('mainr')


class MyPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        if not User.objects.filter(email=form.cleaned_data['email']).exists():
            messages.warning(
                self.request, "email address not found in our database")
            return redirect('password_reset')
        self.request.session['password_reset_requested'] = True
        return super().form_valid(form)


class MyPasswordResetDoneView(PasswordResetDoneView):
    def get(self, request, *args, **kwargs):
        if self.request.session.get('password_reset_requested', False) == True:
            messages.success(
                self.request, "an email has been sent with instructions to reset your password")
            self.request.session['password_reset_requested'] = False
            return redirect('mainr')
        else:
            raise PermissionDenied


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    def form_valid(self, form):
        self.request.session['password_reset_completed'] = True
        return super().form_valid(form)


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    def get(self, request, *args, **kwargs):
        if self.request.session.get('password_reset_completed', False) == True:
            messages.success(self.request, "your password has been set")
            self.request.session['password_reset_completed'] = False
            return redirect('mainr')
        else:
            raise PermissionDenied
