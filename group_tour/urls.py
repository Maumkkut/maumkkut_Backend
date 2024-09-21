from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # group endpoint
    path('', views.GroupView.as_view(), name='group'),
    path('check/', views.CheckGroupName.as_view(), name="group_name"),

    # my_group
    path('list/', views.UserGroupView.as_view(), name="group_list"),

    # group_tour
    path('recommend/', views.RecommendGroupTourListView.as_view(), name="recommend_group_tour_list"),
    path('tour_list/', views.GroupTourListView.as_view(), name="group_tour_list"),
    path('tour_list/like/', views.LikeTourListView.as_view(), name="tour_list_like"),
    path('tour_list/like/group/', views.GroupLikeTourListView.as_view(), name="tour_list_group_like"),

    # like-dislike
    path('like/', views.LikeDislikeView.as_view(), name='like-dislike'),

]