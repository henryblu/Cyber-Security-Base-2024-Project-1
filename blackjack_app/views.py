from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm
from .models import UserProfile

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
