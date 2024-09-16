from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # accounts
    path('', include('dj_rest_auth.urls')),  
    path('registration/', include('dj_rest_auth.registration.urls')), 
    path('add-user-info/', views.AddUserInfo.as_view(), name="add_user_info"),
    path('user-info/', views.UserInfoView.as_view(), name="user_info"), 
    
    # google login endpoint
    path('google/login/', views.google_login, name="google_login"),
    path('google/callback/', views.google_callback, name="google_callback"),
    
    # kakao login endpoint
    path('kakao/login/', views.kakao_login, name="kakao_login"),
    path('kakao/callback/', views.kakao_callback, name="kakao_callback"),
    
    # profile endpoint
    path('check/username/', views.CheckUsername.as_view(), name='check_username'),
    path('check/nickname/', views.CheckNickname.as_view(), name='check_nickname'),

    path('test/', views.TestView.as_view(), name="test")
]