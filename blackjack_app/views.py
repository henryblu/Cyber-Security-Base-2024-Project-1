from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
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
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    context = {
        'user': request.user,
        'games_played': profile.games_played,
        'games_won': profile.games_won,
        'games_lost': profile.games_lost,
    }
    return render(request, 'blackjack_app/profile.html', context)

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
    if blackjack_game_instance.calculate_hand_value(blackjack_game_instance.player_hand) == 21:
        return redirect('dealer_turn')
    if blackjack_game_instance.calculate_hand_value(blackjack_game_instance.dealer_hand) < 17:
        return redirect('determine_winner')
    return redirect('game')

@login_required
def dealer_turn(request):
    global blackjack_game_instance
    blackjack_game_instance.dealer_turn()
    if blackjack_game_instance.is_bust(blackjack_game_instance.dealer_hand) or blackjack_game_instance.calculate_hand_value(blackjack_game_instance.dealer_hand) >= 17:
        return redirect('determine_winner')
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

    profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile.games_played += 1
    if winner == 'Player':
        profile.games_won += 1
    elif winner == 'Dealer':
        profile.games_lost += 1
    profile.save()

    return render(request, 'blackjack_app/game.html', context)

@login_required
def reset_game(request):
    global blackjack_game_instance
    blackjack_game_instance.reset()
    return redirect('start_game')

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home')