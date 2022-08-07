from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from users.models import User, Profile
# use info, success, warning to make it consistent with bootstrap5
from django.contrib import messages
from board.tools import exception_count
from board.models import report_count

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created: 
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    if user.is_public_card_manager: 
        rc = report_count()
        ec = exception_count()
        if rc > 0:
            messages.warning(request, "To Public-Card-Managers: there are "+ str(rc) +" reports to be handled!")
        if ec > 0:
            messages.warning(request, "To Public-Card-Managers: there are "+ str(ec) +" exceptions in the system!")