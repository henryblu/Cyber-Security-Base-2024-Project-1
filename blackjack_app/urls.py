from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('game/', views.game_view, name='game'),
    path('start/', views.start_game, name='start_game'),
    path('hit/', views.player_hit, name='player_hit'),
    path('dealer/', views.dealer_turn, name='dealer_turn'),
    path('winner/', views.determine_winner, name='determine_winner'),
]
