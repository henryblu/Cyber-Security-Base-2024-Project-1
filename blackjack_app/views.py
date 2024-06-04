from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db import connection
from .forms import RegisterForm, LoginForm
from .models import UserProfile
from .blackjack_game.blackjack_game import BlackjackGame

# Initialize a global game object for simplicity
blackjack_game_instance = BlackjackGame()

def welcome(request):
    return render(request, 'blackjack_app/welcome.html')

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
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'blackjack_app/login.html', {'form': form})

@login_required
def home(request):
    return render(request, 'blackjack_app/home.html')

@login_required
def profile(request):
    # Vulnerability #1: Using user input to fetch profile
    profile_id = request.GET.get('profile_id')
    profile = get_object_or_404(UserProfile, id=profile_id)
    # Fix: profile = UserProfile.objects.get(user=request.user)
    context = {
        'user': request.user,
        'games_played': profile.games_played,
        'games_won': profile.games_won,
        'games_lost': profile.games_lost,
        'money': profile.money,
    }
    return render(request, 'blackjack_app/profile.html', context)

@login_required
def start_game(request):
    global blackjack_game_instance
    profile = UserProfile.objects.get(user=request.user)
    profile.in_game = True
    profile.save()
    blackjack_game_instance = BlackjackGame()
    request.session.pop('current_bet', None)
    request.session.pop('cards_dealt', None)
    return redirect('place_bet')

@login_required
def place_bet(request):
    profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        bet = int(request.POST.get('bet', 0))
        if bet > 0 and bet <= profile.money:
            new_money = int(profile.money) - bet
            # Vulnerability #2: Direct SQL update (susceptible to SQL injection)
            with connection.cursor() as cursor:
                cursor.execute("UPDATE blackjack_app_userprofile SET money = %s WHERE id = %s", [new_money, profile.id])
            # Fix: profile.money = new_money
            #      profile.save()
            request.session['current_bet'] = bet
            return redirect('deal_cards')
        else:
            return render(request, 'blackjack_app/place_bet.html', {
                'error': 'Invalid bet. Please enter a valid amount.',
                'money': profile.money
            })
    return render(request, 'blackjack_app/place_bet.html', {'money': profile.money})

@login_required
def deal_cards(request):
    global blackjack_game_instance
    if 'cards_dealt' not in request.session:
        blackjack_game_instance.initial_deal()
        request.session['cards_dealt'] = True
    
    return redirect('game')

@login_required
def game(request):
    profile = UserProfile.objects.get(user=request.user)
    context = {
        'player_hand': blackjack_game_instance.player_hand,
        'dealer_hand': blackjack_game_instance.dealer_hand,
        'player_value': blackjack_game_instance.calculate_hand_value(blackjack_game_instance.player_hand),
        'dealer_value': blackjack_game_instance.calculate_hand_value(blackjack_game_instance.dealer_hand),
        'money': profile.money,
        'current_bet': request.session.get('current_bet', 0),
        'winner': None
    }
    if blackjack_game_instance.is_blackjack():
        return redirect('determine_winner')
    if blackjack_game_instance.is_bust(blackjack_game_instance.player_hand):
        return redirect('determine_winner')
    return render(request, 'blackjack_app/game.html', context)

@login_required
def player_hit(request):
    global blackjack_game_instance
    blackjack_game_instance.player_hit()
    return redirect('game')

@login_required
def dealer_turn(request):
    global blackjack_game_instance
    blackjack_game_instance.dealer_turn()
    return redirect('determine_winner')

@login_required
def determine_winner(request):
    global blackjack_game_instance
    winner = blackjack_game_instance.get_winner()
    blackjack = False
    profile = UserProfile.objects.get(user=request.user)
    current_bet = request.session.get('current_bet', 0)

    # check for blackjack
    new_money = profile.money
    if blackjack_game_instance.is_blackjack():
        blackjack = True
        new_money += current_bet * 2.5
    elif winner == 'Player':
        new_money += current_bet * 2
    elif winner == 'Dealer':
        new_money = new_money

    profile.games_won += 1 if winner == 'Player' or blackjack else 0
    profile.games_lost += 1 if winner == 'Dealer' else 0
    profile.games_played += 1
    profile.in_game = False

    # Vulnerability #2: Direct SQL update (susceptible to SQL injection)
    with connection.cursor() as cursor:
        cursor.execute("UPDATE blackjack_app_userprofile SET money = %s WHERE id = %s", [new_money, profile.id])
    # Fix: profile.money = new_money
    #      profile.save()

    if new_money == 0 or new_money > 1000:
        # vulnerability #1: Using user input to fetch profile
        return redirect(f'place_bet/?profile_id={profile.id}')
        # Fix: return redirect('place_bet')
    
    context = {
        'player_hand': blackjack_game_instance.player_hand,
        'dealer_hand': blackjack_game_instance.dealer_hand,
        'player_value': blackjack_game_instance.calculate_hand_value(blackjack_game_instance.player_hand),
        'dealer_value': blackjack_game_instance.calculate_hand_value(blackjack_game_instance.dealer_hand),
        'money': new_money,
        'winner': winner,
        'blackjack': blackjack,
        'current_bet': current_bet
    }

    return render(request, 'blackjack_app/game.html', context)

@login_required
def reset_game(request):
    global blackjack_game_instance
    blackjack_game_instance.reset()
    return redirect('start_game')

@login_required
def game_over(request):
    # Vulnerability #1: Using user input to fetch profile
    profile_id = request.GET.get('profile_id')
    profile = get_object_or_404(UserProfile, id=profile_id)
    # Fix: profile = UserProfile.objects.get(user=request.user)
    win = False
    
    if profile.money >= 1000:
        win = True
        money = profile.money
        profile.money = 100
        profile.save()
    else:
        user = request.user
        # user.delete()
        auth_logout(request)
        return render(request, 'blackjack_app/game_over.html', {'win': win})

    context = {
        'user': request.user,
        'games_played': profile.games_played,
        'games_won': profile.games_won,
        'games_lost': profile.games_lost,
        'money': money,
        'win': win
    }
    return render(request, 'blackjack_app/game_over.html', context)

@login_required
def logout(request):
    auth_logout(request)
    blackjack_game_instance.reset()
    return redirect('welcome')