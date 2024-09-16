from django.db import models
from accounts.models import Group
from createDB.models import Tours

# Create your models here.
class GroupTourList(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    tour_list = models.ManyToManyField(Tours, through='GroupTourOrder')

class GroupTourOrder(models.Model):
    group_tour_list = models.ForeignKey(GroupTourList, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tours, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = ('group_tour_list', 'tour')
