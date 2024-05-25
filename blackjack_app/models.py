from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)
    in_game = models.BooleanField(default=False)
    money = models.IntegerField(default=100)  # Start with $100

    def __str__(self):
        return self.user.username
