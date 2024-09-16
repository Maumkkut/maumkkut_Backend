from django.db import models
from django.contrib.auth import get_user_model
from createDB.models import Tours

# Create your models here.
User = get_user_model()
class RandomTour(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour_list = models.ManyToManyField(Tours, through='RandomTourOrder')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RandomTourOrder(models.Model):
    random_tour = models.ForeignKey(RandomTour, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tours, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        constraints = [
        models.UniqueConstraint(fields=['random_tour', 'tour'], name='unique_randomtour_tour')
    ]