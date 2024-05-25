from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile, name='profile'),
    path('start_game/', views.start_game, name='start_game'),
    path('place_bet/', views.place_bet, name='place_bet'),
    path('deal_cards/', views.deal_cards, name='deal_cards'),
    path('game/', views.game, name='game'),
    path('hit/', views.player_hit, name='player_hit'),
    path('dealer/', views.dealer_turn, name='dealer_turn'),
    path('winner/', views.determine_winner, name='determine_winner'),
    path('reset/', views.reset_game, name='reset_game'),
    path('logout/', views.logout, name='logout'),
    path('place_bet/', views.place_bet, name='place_bet'),
    path('game_over/', views.game_over, name='game_over')

]
