from re import A
from django.db import models
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from users.models import User
from board.tools import exception_log
import os
# Important concepts:
# - public card / public posts (vs private, by default)
# - approved user to use key features
# - linking cards
# - publishing posts
# - importing posts
# - comments in published posts
# - tags

def filename_gen(userid, filename):
    userid = str(userid)
    res = ""
    for ch in userid:
        res += str(ord(ch))
    res = res[:7]+"_"+filename
    return res

def path_to_imgs(instance, filename):
    path = "uploaded_imgs/"
    newname = filename_gen(instance.author, filename)
    return os.path.join(path, newname)

def path_to_imgs_th(instance, filename):
    path = "uploaded_imgs_th/"
    # newname = filename_gen(instance.author, filename)  # as this add author code twice
    return os.path.join(path, filename)


class Card(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=70)
    desc = models.TextField(blank=True)
    image = models.ImageField(upload_to='uploaded_imgs', blank=True)
    card_color = models.CharField(
        max_length=30, default='rgb(233, 236, 239)')  # gray-200
    is_public = models.BooleanField(default=False)
    # for id of a public card / can link only one card
    linked_card = models.CharField(max_length=10, blank=True)

    # Rules
    # only admin users can make a card public
    # linking a card: a user can link a public card to his/her own card

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('main')


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    content = models.TextField()
    num_images = models.IntegerField(default=0)
    image1 = models.ImageField(upload_to=path_to_imgs, blank=True)
    image2 = models.ImageField(upload_to=path_to_imgs, blank=True)
    image3 = models.ImageField(upload_to=path_to_imgs, blank=True)
    image4 = models.ImageField(upload_to=path_to_imgs, blank=True)
    image5 = models.ImageField(upload_to=path_to_imgs, blank=True)
    image6 = models.ImageField(upload_to=path_to_imgs, blank=True)
    image7 = models.ImageField(upload_to=path_to_imgs, blank=True)

    image1s = models.ImageField(upload_to=path_to_imgs_th, blank=True)
    image2s = models.ImageField(upload_to=path_to_imgs_th, blank=True)
    image3s = models.ImageField(upload_to=path_to_imgs_th, blank=True)
    image4s = models.ImageField(upload_to=path_to_imgs_th, blank=True)
    image5s = models.ImageField(upload_to=path_to_imgs_th, blank=True)
    image6s = models.ImageField(upload_to=path_to_imgs_th, blank=True)
    image7s = models.ImageField(upload_to=path_to_imgs_th, blank=True)

    tags = TaggableManager(blank=True)
    is_published = models.BooleanField(default=False)

    # Rules
    # publishing posts: posts can be published (only) to public cards, and posts in public cards must be (all) publised
    # importing posts: a user can import published posts to his/her own linked card

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs): 
        images = [self.image1, self.image2, self.image3, self.image4, self.image5, self.image6, self.image7]
        th_images = [self.image1s, self.image2s, self.image3s, self.image4s, self.image5s, self.image6s, self.image7s]
        for i in range(0, 7):
            try:
                if images[i].name != "":
                    images[i].delete()
            except:
                text = "Exception in delete images - class Post delete(): " + images[i].name
                print(text)
                exception_log(text)

            try:
                if th_images[i].name != "":
                    th_images[i].delete()
            except:
                text = "Exception in delete th_images - class Post delete(): "+ th_images[i].name  
                print(text)
                exception_log(text)

        return super().delete(*args, **kwargs)

    def get_preview_text(self):
        res = ' '.join(self.content[:150].split('\n')[:3])
        return res

    def __str__(self):
        return self.get_preview_text()

    class Meta:
        None

    def get_absolute_url(self):
        return reverse('card-content', kwargs={'card_id': self.card.id})
