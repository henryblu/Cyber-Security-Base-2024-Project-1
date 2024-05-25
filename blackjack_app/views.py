from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import UserProfile
from .blackjack_game.blackjack_game import BlackjackGame

# Initialize a global game object (for simplicity)
blackjack_game_instance = BlackjackGame()

def home(request):
    return render(request, 'blackjack_app/home.html')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'blackjack_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('game')
    else:
        form = LoginForm()
    return render(request, 'blackjack_app/login.html', {'form': form})

@login_required
def profile(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'blackjack_app/profile.html', {'profile': profile})

@login_required
def game(request):
    return render(request, 'blackjack_app/game.html')

@login_required
def start_game(request):
    global blackjack_game_instance
    blackjack_game_instance = BlackjackGame()
    blackjack_game_instance.initial_deal()
    return redirect('game')

@login_required
def game_view(request):
    context = {
        'player_hand': blackjack_game_instance.player_hand,
        'dealer_hand': blackjack_game_instance.dealer_hand,
        'player_value': blackjack_game_instance.calculate_hand_value(blackjack_game_instance.player_hand),
        'dealer_value': blackjack_game_instance.calculate_hand_value(blackjack_game_instance.dealer_hand),
        'winner': None,
        'is_player_bust': blackjack_game_instance.is_bust(blackjack_game_instance.player_hand)
    }
    if context['is_player_bust']:
        context['winner'] = 'Dealer'
    return render(request, 'blackjack_app/game.html', context)


@login_required
def player_hit(request):
    global blackjack_game_instance
    blackjack_game_instance.player_hit()
    if blackjack_game_instance.is_bust(blackjack_game_instance.player_hand):
        return redirect('game')
    return redirect('game')


@login_required
def dealer_turn(request):
    global blackjack_game_instance
    blackjack_game_instance.dealer_turn()
    return redirect('game')


@login_required
def determine_winner(request):
    global blackjack_game_instance
    winner = blackjack_game_instance.get_winner()
    context = {
        'player_hand': blackjack_game_instance.player_hand,
        'dealer_hand': blackjack_game_instance.dealer_hand,
        'player_value': blackjack_game_instance.calculate_hand_value(blackjack_game_instance.player_hand),
        'dealer_value': blackjack_game_instance.calculate_hand_value(blackjack_game_instance.dealer_hand),
        'winner': winner,
    }
    return render(request, 'blackjack_app/game.html', context)

