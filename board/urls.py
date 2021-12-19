from django.urls import path
from board.views import *

urlpatterns = [
  path('', index_view, name='main'), 
]
