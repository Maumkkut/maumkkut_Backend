from rest_framework import serializers
from createDB.models import Tours

class TypeTourListSerializer(serializers.ModelSerializer):
    tour_id = serializers.IntegerField(source='id')
    class Meta:
        model = Tours
        fields = ['tour_id', 'addr1', 'title', 'mapx', 'mapy', 'image']

class FestivalListSerializer(serializers.ModelSerializer):
    tour_id = serializers.IntegerField(source='id')
    class Meta:
        model = Tours
        fields = ['tour_id', 'title', 'image']