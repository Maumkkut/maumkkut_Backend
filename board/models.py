from django.conf import settings
from django.db import models

class Post(models.Model):
    BOARD_CHOICES = [
        ('free', '자유게시판'),
        ('travel', '여행 후기 게시판'),
        ('notice', '공지사항 게시판'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    report_count = models.IntegerField(default=0)  # 신고 횟수
    is_reported = models.BooleanField(default=False)  # 신고 상태
    board_type = models.CharField(max_length=20, choices=BOARD_CHOICES, default='free')  # 게시판 타입

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    report_count = models.IntegerField(default=0)  # 신고 횟수
    is_reported = models.BooleanField(default=False)  # 신고 상태
    parent_comment = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    # parent_comment 필드가 대댓글임, 자기 자신을 참조할 수 있도록 설정

