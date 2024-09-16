from django.db import models
from accounts.models import Group
from createDB.models import Tours
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

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

User = get_user_model()
class LikeDislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tours, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=False)
    is_disliked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # 유저는 한 여행지에 한 번만 좋아요/싫어요 가능
    class Meta:
        unique_together = ('user', 'tour')  

    def clean(self):
        # 좋아요와 싫어요가 동시에 True일 수 없도록 검증
        if self.is_liked and self.is_disliked:
            raise ValidationError("좋아요와 싫어요를 동시에 선택할 수 없습니다.")

    def save(self, *args, **kwargs):
        self.clean()  # 저장하기 전 검증
        super().save(*args, **kwargs)