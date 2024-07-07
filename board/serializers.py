from rest_framework import serializers
from .models import Post, Comment

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at', 'replies']
        read_only_fields = ['author', 'created_at']

    def get_replies(self, obj):
        replies_queryset = Comment.objects.filter(parent_comment=obj)
        replies_serializer = CommentSerializer(replies_queryset, many=True)
        return replies_serializer.data

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'comments']
        read_only_fields = ['author', 'created_at']
