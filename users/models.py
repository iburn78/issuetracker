from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from board.tools import exception_log
DEFAULT_PIC = "default_user.png"

class User(AbstractUser):
    is_approved = models.BooleanField(default=False) # Not yet used... 
    is_public_card_manager = models.BooleanField(default=False)

class Profile(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default=DEFAULT_PIC, upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
            
    def last_login(self):
        return self.user.last_login.strftime("%Y-%m-%d, %H:%M:%S")

    def delete(self, *args, **kwargs): 
        name = str(self.image.name)
        try:
            image_file_name = os.path.basename(self.image.name)
            if image_file_name != DEFAULT_PIC:
                self.image.delete()
        except:
            text = "Exception in deleting image - class Profile delete(): " + name
            exception_log(text)
        return super().delete(*args, **kwargs)

