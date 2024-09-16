# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
# default user model
# username(id), password1, password2, email
# 추가 필드
# name, phone_number, address, nickname, date_of_birth

class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_GROUP_LEADER = 'group_leader'
    ROLE_GROUP_MEMBER = 'group_member'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_GROUP_LEADER, 'Group Leader'),
        (ROLE_GROUP_MEMBER, 'Group Member'),
    ]
    name = models.CharField(max_length=10, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    nickname = models.CharField(max_length=10, blank=True, null=True, unique=True)
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="생년월일")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_GROUP_MEMBER)

    
    # 디버깅용
    def __str__(self):
        return self.username
    
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    def is_group_leader(self):
        return self.role == self.ROLE_GROUP_LEADER

    def is_group_member(self):
        return self.role == self.ROLE_GROUP_MEMBER
    
class Group(models.Model):
    name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(User, related_name='group_member')
    leader = models.ForeignKey(User, related_name='group_leader', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    region = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.name

    # 유저 조회
    def get_members_with_leader(self):
        members = list(self.members.all())
        if self.leader not in members:
            members.append(self.leader)
        return members

    # 유저 확인
    def is_user_in_group(self, user):
        return self.members.filter(id=user.id).exists()

    # 유저 추가
    def add_member(self, user):
        if not self.is_user_in_group(user):
            self.members.add(user)

    # 유저 제거
    def remove_member(self, user):
        if self.is_user_in_group(user):
            self.members.remove(user)

    @classmethod
    def get_groups_for_user(cls, user_id):
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return cls.objects.none()  # 빈 쿼리셋 반환
        
        # 유저가 멤버인 그룹과 리더인 그룹 모두 조회
        return cls.objects.filter(members=user).distinct() | cls.objects.filter(leader=user).distinct()