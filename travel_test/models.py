from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class TravelTest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    character_type = models.CharField(max_length=255)
    character_description = models.TextField()
    recommend_place = models.CharField(max_length=10)
    recommend_reason = models.TextField()
    best_match = models.CharField(max_length=20)
    match_reason = models.TextField()