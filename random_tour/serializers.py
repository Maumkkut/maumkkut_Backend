from rest_framework import serializers
from django.contrib.auth import get_user_model
from createDB.models import Tours
from .models import RandomTour, RandomTourOrder

# class RandomTourSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RandomTour
#         fields = ['id', 'title', 'addr1', 'mapx', 'mapy']

class SaveRandomTourOrderSerializer(serializers.ModelSerializer):
    tour_id = serializers.IntegerField(source='tour.id')
    tour_name = serializers.CharField(source='tour.title')
    tour_address = serializers.CharField(source='tour.addr1')
    tour_mapx = serializers.IntegerField(source='tour.mapx')
    tour_mapy = serializers.IntegerField(source='tour.mapy')

    class Meta:
        model = RandomTourOrder
        fields = ['order', 'tour_id', 'tour_name', 'tour_address', 'tour_mapx', 'tour_mapy']

class SaveRandomTourListSerializer(serializers.ModelSerializer):
    tour_list = SaveRandomTourOrderSerializer(many=True, source='randomtourorder_set', read_only=True)
    course_id = serializers.IntegerField(source='id')

    class Meta:
        model = RandomTour
        fields = ['course_id', 'tour_list']

class RandomOrderSerializer(serializers.Serializer):
    order = serializers.IntegerField()
    tour_id = serializers.IntegerField()
    tour_name = serializers.CharField()
    tour_address = serializers.CharField()
    tour_mapx = serializers.IntegerField()
    tour_mapy = serializers.IntegerField()

class RandomListSerializer(serializers.Serializer):
    tour_list = RandomOrderSerializer(many=True)
