"""
URL configuration for core app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('game/', views.game, name='game'),
    path('api/start/', views.start_game, name='start_game'),
    path('api/state/', views.get_state, name='get_state'),
    path('api/move/left/', views.move_left, name='move_left'),
    path('api/move/right/', views.move_right, name='move_right'),
    path('api/move/down/', views.move_down, name='move_down'),
    path('api/hard-drop/', views.hard_drop, name='hard_drop'),
    path('api/rotate/', views.rotate, name='rotate'),
    path('api/hold/', views.hold, name='hold'),
    path('api/pause/', views.toggle_pause, name='toggle_pause'),
    path('api/therapist/roast/', views.get_therapist_roast, name='get_roast'),
    path('api/therapist/report/', views.get_final_report, name='get_report'),
]

