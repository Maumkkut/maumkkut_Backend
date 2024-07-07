"""
URL configuration for maumkkut project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views
from django.urls import path

urlpatterns = [
    path('posts/', views.post_list, name='post-list'),
    path('posts/day/', views.post_list_day, name='post-list-day'),
    path('posts/week/', views.post_list_week, name='post-list-week'),
    path('posts/month/', views.post_list_month, name='post-list-month'),
    path('posts/year/', views.post_list_year, name='post-list-year'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/search/', views.search_posts, name='search_posts'),
    path('posts/<int:post_id>/comments/', views.comment_list, name='comment_list'),
    path('posts/<int:post_id>/comments/<int:comment_id>/', views.comment_operations, name='comment_operations'),
    path('posts/<int:post_id>/comments/<int:comment_id>/detail/', views.comment_detail, name='comment_detail'),
    path('posts/<int:post_id>/report/', views.report_post, name='report-post'),
    path('comments/<int:comment_id>/report/', views.report_comment, name='report-comment'),

]