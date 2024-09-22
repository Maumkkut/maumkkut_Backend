# serializers.py

from rest_framework import serializers
from board.models import Post, Comment
from django.utils import timezone
from datetime import timedelta

class UserPostSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'board_type']

    def get_created_at(self, obj):
        now = timezone.now()
        time_diff = now - obj.created_at

        if time_diff < timedelta(hours=24):
            hours = int(time_diff.total_seconds() // 3600)
            if hours == 0:
                minutes = int(time_diff.total_seconds() // 60)
                if minutes == 0:
                    return "방금 전"
                else:
                    return f"{minutes}분 전"
            else:
                return f"{hours}시간 전"
        else:
            if obj.created_at.year == now.year:
                if obj.created_at.month == now.month:
                    return f"{obj.created_at.day}일 전"
                else:
                    return f"{obj.created_at.month}월 전"
            else:
                return f"{obj.created_at.year}년 전"

class UserCommentSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source='post.title', read_only=True)
    post_id = serializers.IntegerField(source='post.id', read_only=True)
    board_type = serializers.CharField(source='post.board_type', read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'post_title', 'post_id', 'created_at', 'board_type']

    def get_created_at(self, obj):
        now = timezone.now()
        time_diff = now - obj.created_at

        if time_diff < timedelta(hours=24):
            hours = int(time_diff.total_seconds() // 3600)
            if hours == 0:
                minutes = int(time_diff.total_seconds() // 60)
                if minutes == 0:
                    return "방금 전"
                else:
                    return f"{minutes}분 전"
            else:
                return f"{hours}시간 전"
        else:
            if obj.created_at.year == now.year:
                if obj.created_at.month == now.month:
                    return f"{obj.created_at.day}일 전"
                else:
                    return f"{obj.created_at.month}월 전"
            else:
                return f"{obj.created_at.year}년 전"
            