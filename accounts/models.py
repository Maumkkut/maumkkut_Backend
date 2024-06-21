from django.db import models
from django.contrib.auth.models import AbstractUser

# default user model
# username(id), password1, password2, email

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="생년월일")

    # 디버깅용
    def __str__(self):
        return self.username