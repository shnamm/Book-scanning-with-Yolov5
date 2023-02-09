from django.urls import path
from rest_framework import routers
from django.urls import path, include
from . import views

#from pybo import views

urlpatterns = [
    path('', views.index,name="home"),
    path('<int:image_id>/', views.detail),
    path('<str:book_title>/', views.inform),
]