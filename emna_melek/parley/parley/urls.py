from django.contrib import admin
from django.urls import path
from app.views import index, chat_api, evaluate_api

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('api/chat/', chat_api, name='chat_api'),
    path('api/evaluate/', evaluate_api, name='evaluate_api'),
]
