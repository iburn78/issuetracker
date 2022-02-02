from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from users.models import User

DEFAULT_CARD_COLOR = 'bg-primary'

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
    image = models.ImageField(upload_to='post_imgs', blank=True)
    card_color = models.CharField(max_length=30, default=DEFAULT_CARD_COLOR)
    is_public = models.BooleanField(default=False)
    linked_card = models.CharField(max_length=10) # for id of a public card / can link only one card

    # Rules
    # only admin users can make a card public 
    # linking a card: a user can link a public card to his/her own card

    def __str__(self):
        return self.title


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    content = models.TextField()
    image = models.ImageField(upload_to='post_imgs', blank=True)
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

