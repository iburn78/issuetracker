from django.urls import path
from board.views import *

urlpatterns = [
  path('about/', about, name='about'), 
  path('', index_view, name='main'), 
]
