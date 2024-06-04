# blackjack_app/context_processors.py

from .models import UserProfile

def game_state(request):
    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        return {
            'in_game': profile.in_game,
            'profile_id': profile.id,
        }

    return {'in_game': False}
