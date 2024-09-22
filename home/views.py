from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from createDB.DataProcessing.RandomRoute import random_tour_type
from createDB.DataProcessing.FilterName import filter_type
from random_tour.translation_region_code import get_region_code
# Create your views here.
class TypeView(APIView):

    def get(request, self):
        area_code = get_region_code("양양")
        test = filter_type(area_code, "나무늘보형 순두부")
        print(test, len(test))
        return Response({
            "data": test
        }, status=status.HTTP_200_OK)