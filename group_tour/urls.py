from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # group endpoint
    path('', views.GroupView.as_view(), name='group'),

    # group_tour
    path('list/', views.UserGroupView.as_view(), name="group_list")

    
]