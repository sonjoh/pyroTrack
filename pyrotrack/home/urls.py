# django urls.py

# Path: pyrotrack/home/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('', views.index, name='index'),
]
