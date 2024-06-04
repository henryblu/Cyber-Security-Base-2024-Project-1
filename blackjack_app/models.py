from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)
    money = models.DecimalField(max_digits=10, decimal_places=0, default=100)
    in_game = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile (User ID: {self.user.id})"
