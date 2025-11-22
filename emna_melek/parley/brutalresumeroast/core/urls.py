"""
URL configuration for core app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('favicon.ico', views.favicon, name='favicon'),
    path('upload/', views.upload_resume, name='upload'),
    path('roast/<str:task_id>/', views.roast_page, name='roast'),
    path('roast/<str:task_id>/status/', views.roast_status, name='roast_status'),
]

