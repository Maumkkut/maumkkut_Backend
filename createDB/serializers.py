from rest_framework import serializers
from .models import Tours

class TourSerializer(serializers.ModelSerializer):
  class Meta:
    model: Tours
    fields ='__all__'