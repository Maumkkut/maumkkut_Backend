from ..models import Tours
import json
import random
from django.core import serializers
from .FilterName import filter_type

def random_area(areacode):
    tour_data = Tours.objects.filter(sigungucode=areacode)
    random_tour_data = random.sample(list(tour_data), min(len(tour_data), 5))
    random_data_json = json.loads(serializers.serialize('json', random_tour_data))
    return random_data_json


def random_tour_type(areacode, tour_type):
    tour_data = filter_type(areacode, tour_type)
    if tour_data:
        random_tour_data = random.sample(list(tour_data), min(len(tour_data), 5))
        random_data_json = json.loads(serializers.serialize('json', random_tour_data))
    else:
        random_data_json = '여행 유형 입력이 올바르지 않습니다.'
    return random_data_json