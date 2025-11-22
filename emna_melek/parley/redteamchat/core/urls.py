from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_document, name='upload'),
    path('chat/', views.chat, name='chat'),
    path('toggle-mode/', views.toggle_mode, name='toggle_mode'),
]
