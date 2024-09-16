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
            return obj.created_at.strftime('%Y-%m-%d')

class UserCommentSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source='post.title', read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'post_title', 'created_at']

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
            return obj.created_at.strftime('%Y-%m-%d')
