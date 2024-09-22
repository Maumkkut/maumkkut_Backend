from django.urls import path, include
from . import views

urlpatterns = [
    # kangwondo
    path('type/', views.TypeView.as_view(), name='type'),
]