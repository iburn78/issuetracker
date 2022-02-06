from django.urls import path
from board.views.card_view import *
from board.views.post_view import *

urlpatterns = [
  path('', CardListView.as_view(), name='main'), 
  path('about/', about, name='about'), 
  path('card/new/', CardCreateView.as_view(), name='card-create'),
  path('card/<int:pk>/', CardContentListView.as_view(), name='card-content'),
  path('card/<int:card_id>/post/new/', PostCreateView.as_view(), name='post-create'),
  path('card/<int:card_id>/post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
]