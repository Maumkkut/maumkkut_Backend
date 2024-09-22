from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from createDB.DataProcessing.FilterName import filter_type
from .serializers import TypeTourListSerializer, FestivalListSerializer
import random
from itertools import chain
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from createDB.models import Tours
# Create your views here.

class TypeView(APIView):
    @swagger_auto_schema(
            operation_summary="여행 유형별 여행지 리스트 조회",
            operation_description="여행 유형별 여행지를 16개 추천해드립니다.",
            manual_parameters=[
                openapi.Parameter(
                    'travel_type', 
                    openapi.IN_QUERY, 
                    description="travel_type", 
                    type=openapi.TYPE_STRING,
                    required=True
                ),
            ],
            responses={
                200: openapi.Response(
                    description="조회 성공",
                    examples={
                        "application/json": {
                            "message": "유형별 추천 여행지 목록을 조회합니다.",
                            "result": [
                            {
                                "tour_id": 3812,
                                "addr1": "강원특별자치도 철원군 동송읍 태봉로 1825",
                                "title": "철원관광정보센터",
                                "mapx": 127.2868693456,
                                "mapy": 38.1859626462,
                                "image": ""
                            },
                            {
                                "tour_id": 1485,
                                "addr1": "강원특별자치도 영월군 수주면 무릉법흥로 1352",
                                "title": "법흥사(영월)",
                                "mapx": 128.2610687984,
                                "mapy": 37.3717392902,
                                "image": ""
                            }
                            ]
                        }
                    }
                )
                ,
                400: openapi.Response(
                    description="조회 실패",
                    examples={
                        "application/json": {
                            "message": "region, travel_type을 확인하세요."
                        }
                    }
                )
            }
        )
    def get(self, request):
        travel_type = request.GET.get('travel_type')
        if not travel_type:
            return Response({
                "message": "region, travel_type을 확인하세요."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        total_tour = []

        # 1부터 18까지 지역 코드
        for area_code in range(1, 19):
            tour_list = filter_type(area_code, travel_type) 
            total_tour.append(tour_list)

        # QuerySet 연결
        combined_tour_list = list(chain.from_iterable(total_tour))

        random_tours = random.sample(combined_tour_list, min(len(combined_tour_list), 10))

        serializer = TypeTourListSerializer(random_tours, many=True)


        return Response({
            "message": "유형별 추천 여행지 목록을 조회합니다.",
            "result": serializer.data
        }, status=status.HTTP_200_OK)
    
class FestivalView(APIView):
    @swagger_auto_schema(
            operation_summary="강원도 축제 리스트 조회",
            operation_description="강원도 축제 리스트를 9개 조회합니다.",
            responses={
                200: openapi.Response(
                    description="조회 성공",
                    examples={
                        "application/json": {
                        "message": "강원도 축제 목록을 조회합니다.",
                        "result": [
                            {
                                "tour_id": 169,
                                "title": "강릉커피축제",
                                "image": "http://tong.visitkorea.or.kr/cms/resource/83/3020283_image2_1.png"
                            },
                            {
                                "tour_id": 3205,
                                "title": "원주용수골가을꽃축제",
                                "image": "http://tong.visitkorea.or.kr/cms/resource/72/3011172_image2_1.jpg"
                            },
                        ]
                        }
                    }
                )
                ,
            }
        )
    def get(self, request):
        festival_obj = Tours.objects.filter(type_id=15).order_by('?')[:9]
        serializer = FestivalListSerializer(festival_obj, many=True)
        return Response({
            "message": "강원도 축제 목록을 조회합니다.",
            "result": serializer.data
        }, status=status.HTTP_200_OK)
