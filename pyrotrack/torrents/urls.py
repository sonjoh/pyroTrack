from django.urls import path
from . import views

urlpatterns = [
    path('announce', views.announce, name='announce'),
    path('scrape', views.scrape, name='scrape'),
    path('upload/', views.upload_torrent, name='upload_torrent'),
]