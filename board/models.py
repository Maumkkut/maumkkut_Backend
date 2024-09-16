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
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    report_count = models.IntegerField(default=0, db_index=True)
    is_reported = models.BooleanField(default=False, db_index=True)
    board_type = models.CharField(max_length=20, choices=BOARD_CHOICES, default='free', db_index=True)
    liked_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at', 'board_type']),  # 복합 인덱스 추가
        ]


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    report_count = models.IntegerField(default=0, db_index=True)
    is_reported = models.BooleanField(default=False, db_index=True)
    parent_comment = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
