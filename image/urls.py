from django.urls import path
from . import views

#from pybo import views

urlpatterns = [
    path('', views.index,name="home"),
    path('<int:image_id>/', views.detail),
    path('<str:book_title>/', views.inform),
]