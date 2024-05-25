from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
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
    profile = UserProfile.objects.get_or_create(user=request.user)[0]
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
            profile.money -= bet
            profile.save()
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
    if blackjack_game_instance.is_blackjack():
        blackjack = True
        profile.money += current_bet * 2.5
        profile.games_won += 1
    elif winner == 'Player':
        profile.money += current_bet * 2
        profile.games_won += 1
    elif winner == 'Dealer':
        profile.games_lost += 1

    profile.games_played += 1
    profile.save()
    
    if profile.money == 0 or profile.money > 1000:
        return redirect('game_over')
    
    context = {
        'player_hand': blackjack_game_instance.player_hand,
        'dealer_hand': blackjack_game_instance.dealer_hand,
        'player_value': blackjack_game_instance.calculate_hand_value(blackjack_game_instance.player_hand),
        'dealer_value': blackjack_game_instance.calculate_hand_value(blackjack_game_instance.dealer_hand),
        'money': profile.money,
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
    profile = UserProfile.objects.get(user=request.user)
    win = False
    message = ""
    
    if profile.money >= 1000:
        message = "Congratulations! You've reached $1,000! Please contact support to claim your mysterious prize."
        win = True
        money = profile.money
        profile.money = 100
        profile.save()
    elif profile.money <= 0:
        message = "You've run out of money. Your account will now be deleted."
        win = False
        user = request.user
        # user.delete()
        auth_logout(request)
        return render(request, 'blackjack_app/game_over.html', {'win': win})
    else:
        return redirect('home')

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