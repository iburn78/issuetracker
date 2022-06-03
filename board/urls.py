from django.urls import path
from board.views.card_view import *
from board.views.post_view import *
from django.conf import settings
from django.views.generic import RedirectView
from board.tools import *
from os.path import join


urlpatterns = [
    path('', CardListView.as_view(revisit=False, card_list=True), name='main'),
    path('main/', CardListView.as_view(revisit=True, card_list=True), name='mainr'),
    path('card_list/', CardListView.as_view(template_name="board/card_list.html", card_list=False), name='card-list'),
    path('card_select/', CardSelectView.as_view(), name='card-select'),
    path('about/', about, name='about'),
    path('new_card/', CardCreateView.as_view(), name='card-create'),
    path('card/<int:card_id>/', CardContentListView.as_view(), name='card-content'),
    path('card/<int:pk>/update/', CardUpdateView.as_view(), name='card-update'),
    path('card/<int:pk>/delete/', CardDeleteView.as_view(), name='card-delete'),
    path('card/<int:card_id>/new_post/', PostCreateView.as_view(), name='post-create'),
    path('post_delete/<int:pk>/', PostDeleteView.as_view(), name='post-delete'),
    path('post_update/<int:pk>/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL+'board/IssueTracker_Logo.png')),
    path(join('media', POST_UPLOADED_IMGS, '<str:file>'), PostMediaView.as_view(), name='media-view'),
    path(join('media', POST_UPLOADED_IMGS_RESIZED, '<str:file>'), PostMediaView.as_view(), name='media-view'),
    path(join('media', CARD_UPLOADED_IMGS, '<str:file>'), CardMediaView.as_view(), name='media-view'),
]
