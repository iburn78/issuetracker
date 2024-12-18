from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from board.tools import *
from django.conf import settings
from random import choice, randint
from os.path import join as path_join
from os import listdir
from os.path import isfile
from django.utils import timezone

def random_user_img():
    dir_path = path_join(settings.MEDIA_ROOT, USER_DEFAULT_IMAGES)
    files = [content for content in listdir(dir_path) if isfile(path_join(dir_path, content))]
    return path_join(USER_DEFAULT_IMAGES, choice(files))

def path_to_user_imgs(instance, filename): 
    path = PROFILE_PICS
    _, ext = os.path.splitext(filename)
    newname = f"profile_pic_{instance.user.id}_{str(randint(10000, 99999))}{ext}"
    return os.path.join(path, newname)

class User(AbstractUser):
    is_VIP = models.BooleanField(default=False) # Not yet used... 
    is_public_card_manager = models.BooleanField(default=False)
    is_in_private_mode = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        self.profile.delete()
        return super().delete(*args, **kwargs)

class Profile(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default=random_user_img, upload_to=path_to_user_imgs)

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
            
    def last_login(self):
        return timezone.localtime(self.user.last_login).strftime("%Y-%m-%d, %H:%M:%S")

    def delete(self, *args, **kwargs): 
        name = str(self.image.name)
        try:
            image_dir_name = os.path.basename(os.path.dirname(self.image.name))
            if image_dir_name != USER_DEFAULT_IMAGES:
                self.image.delete()
        except:
            text = "Exception in deleting image - class Profile delete(): " + name
            exception_log(text)
        return super().delete(*args, **kwargs)

