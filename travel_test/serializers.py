from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TravelTest

class TestResultSerializer(serializers.ModelSerializer):
    test_id = serializers.IntegerField(source='id')
    class Meta:
        model = TravelTest
        fields = ['test_id', 'character_type', 'character_description', 'recommend_place', 'recommend_reason', 'best_match', 'match_reason']

class TestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelTest
        fields = ['id', 'character_type', 'created_at']