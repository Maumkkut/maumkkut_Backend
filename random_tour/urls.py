from django.urls import path, include
from . import views

urlpatterns = [
    # random endpoint
    path('', views.RandomView.as_view(), name='random'),
    path('course/', views.CourseView.as_view(), name='random'),
    # path('list/', views.RandomView.as_view(), name='test_list')
]