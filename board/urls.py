from django.urls import path
from board.views.card_view import *
from board.views.post_view import *

urlpatterns = [
    path('', CardListView.as_view(revisit=False), name='main'),
    path('main/', CardListView.as_view(revisit=True), name='mainr'),
    path('about/', about, name='about'),
    path('card/new/', CardCreateView.as_view(), name='card-create'),
    path('card/<int:card_id>/', CardContentListView.as_view(), name='card-content'),
    path('card/<int:pk>/update/', CardUpdateView.as_view(), name='card-update'),
    path('card/<int:pk>/delete/', CardDeleteView.as_view(), name='card-delete'),
    path('card/<int:card_id>/post/new/',
         PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
]
