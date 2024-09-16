# posts/urls.py
from django.urls import path
from .views import (
    user_post_list,
    user_comment_list,
    user_content_count,
    user_liked_posts,
)

urlpatterns = [
    path('user/posts/', user_post_list, name='user-posts'),
    path('user/comments/', user_comment_list, name='user-comments'),
    path('user/counts/', user_content_count, name='user-content-counts'),
    path('user/liked-posts/', user_liked_posts, name='user-liked-posts'),
]
