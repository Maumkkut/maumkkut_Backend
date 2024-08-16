from rest_framework import serializers
from .models import Post, Comment
from drf_yasg.utils import swagger_serializer_method
from accounts.models import User

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author_username', 'created_at', 'replies']
        read_only_fields = ['author_username', 'created_at']

    @swagger_serializer_method(serializer_or_field=serializers.ListSerializer(child=serializers.IntegerField()))
    def get_replies(self, obj):
        replies_queryset = Comment.objects.filter(parent_comment=obj)
        replies_serializer = CommentSerializer(replies_queryset, many=True)
        return replies_serializer.data

class PostListSerializer(serializers.ModelSerializer):
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    board_type = serializers.ChoiceField(choices=Post.BOARD_CHOICES, default='free')
    author_username = serializers.CharField(source='author.username', read_only=True)
    liked_users_count = serializers.IntegerField(source='liked_users.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author_username', 'created_at', 'board_type', 'comment_count', 'liked_users_count']
        read_only_fields = ['author_username', 'created_at']

class PostDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    board_type = serializers.ChoiceField(choices=Post.BOARD_CHOICES, default='free')
    author_username = serializers.CharField(source='author.username', read_only=True)
    liked_users_count = serializers.IntegerField(source='liked_users.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author_username', 'created_at', 'board_type', 'comments', 'liked_users_count']
        read_only_fields = ['author_username', 'created_at']
