from django.db import models
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from users.models import User

# Important concepts: 
# - public card / public posts (vs private, by default)
# - approved user to use key features
# - linking cards
# - publishing posts
# - importing posts
# - comments in published posts
# - tags

class Card(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=70)
    desc = models.TextField(blank=True)
    image = models.ImageField(upload_to='uploaded_imgs', blank=True)
    card_color = models.CharField(max_length=30, default='rgb(233, 236, 239)') # gray-200
    is_public = models.BooleanField(default=False)
    linked_card = models.CharField(max_length=10, blank=True) # for id of a public card / can link only one card

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
    image1 = models.ImageField(upload_to='uploaded_imgs', blank=True)
    image2 = models.ImageField(upload_to='uploaded_imgs', blank=True)
    image3 = models.ImageField(upload_to='uploaded_imgs', blank=True)
    tags = TaggableManager(blank=True)
    is_published  = models.BooleanField(default=False)
    imported_authors = [] # to include objects of User

    # Rules
    # publishing posts: posts can be published (only) to public cards, and posts in public cards must be (all) publised
    # importing posts: a user can import published posts to his/her own linked card 

    def get_preview_text(self):
        return self.content[:70]

    def __str__(self):
        return self.get_preview_text()

    class Meta:
        # abstract = True
        None

    def get_absolute_url(self):
        return reverse('main')
