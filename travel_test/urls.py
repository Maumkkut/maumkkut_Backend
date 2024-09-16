from django.urls import path, include
from . import views

urlpatterns = [
    # test endpoint
    path('', views.TravelTestView.as_view(), name='test'),
    path('list/', views.TravelTestListView.as_view(), name='test_list')
]