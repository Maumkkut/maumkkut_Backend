from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from createDB.DataProcessing.FilterName import filter_type
from .serializers import RandomListSerializer, SaveRandomTourListSerializer, RandomTourSerializer
from .models import RandomTour, RandomTourOrder
from travel_test.models import TravelTest
from .translation_region_code import get_region_code
from createDB.models import Tours
from django.shortcuts import get_object_or_404
# Create your views here.
class RandomView(APIView):

    # 랜덤 여행 코스 추천
    @swagger_auto_schema(
        operation_summary="랜덤 여행 코스 추천",
        operation_description="랜덤으로 여행 코스를 5개 추천합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'region': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['region']
        ),
        responses={
            200: openapi.Response(
                description="랜덤 여행 코스 추천 성공",
                examples={
                    "application/json": {
                        "message": "랜덤으로 여행지를 추천합니다.",
                        "result": {
                            "tour_list": [
                                {
                                    "order": 1,
                                    "tour_id": 1705,
                                    "tour_name": "비치얼스",
                                    "tour_address": "강원특별자치도 양양군 현북면 하조대4길 32 3층",
                                    "tour_mapx": 128,
                                    "tour_mapy": 38
                                },
                                {
                                    "order": 2,
                                    "tour_id": 4736,
                                    "tour_name": "헬로피스카페",
                                    "tour_address": "강원특별자치도 양양군 현북면 하조대2길 48-34 1층",
                                    "tour_mapx": 128,
                                    "tour_mapy": 38
                                },
                                {
                                    "order": 3,
                                    "tour_id": 2643,
                                    "tour_name": "양양 탁장사마을",
                                    "tour_address": "강원특별자치도 양양군 현북면 어성전길 256",
                                    "tour_mapx": 128,
                                    "tour_mapy": 37
                                },
                                {
                                    "order": 4,
                                    "tour_id": 2656,
                                    "tour_name": "양양전통시장 (4, 9일)",
                                    "tour_address": "강원특별자치도 양양군 양양읍 남문5길 4-1",
                                    "tour_mapx": 128,
                                    "tour_mapy": 38
                                },
                                {
                                    "order": 5,
                                    "tour_id": 2009,
                                    "tour_name": "설온",
                                    "tour_address": "강원특별자치도 양양군 강현면 복골길201번길 58",
                                    "tour_mapx": 128,
                                    "tour_mapy": 38
                                }
                            ]
                        }
                    }
                }
            ),
            400: openapi.Response(              description="지역 조회 실패",
                examples={
                    "application/json": {
                        "message": "올바르지 않은 지역입니다."
                    }
                }
            ),
            404: openapi.Response(              description="여행 취향 테스트 결과 없음",
                examples={
                    "application/json": {
                        "message": "여행 취향 테스트 결과가 없습니다."
                    }
                }
            ),
        }
    )
    def post(self, request):
        # 지역 조회
        region = request.data.get('region')
        areacode = get_region_code(region)
        if not areacode:
            return Response({
            "message": "올바르지 않은 지역입니다.",
        }, status=status.HTTP_400_BAD_REQUEST)

        # 캐릭터 타입 조회
        travel_test = TravelTest.objects.filter(user=request.user).order_by('-created_at').first()
        if not travel_test:
            return Response({
            "message": "여행 취향 테스트 결과가 없습니다.",
        }, status=status.HTTP_404_NOT_FOUND)

        tour_type = travel_test.character_type
        tour_data = filter_type(areacode, tour_type).order_by('?')[:5]

        tour_list_data = [
        {
            "order": idx + 1,
            "tour_id": tour.id,
            "tour_name": tour.title,
            "tour_address": tour.addr1,
            "tour_mapx": tour.mapx,
            "tour_mapy": tour.mapy,
        }
        for idx, tour in enumerate(tour_data)
    ]
    
        serializer = RandomListSerializer({"tour_list": tour_list_data})
        
        return Response({
            "message": "랜덤으로 여행지를 추천합니다.",
            "result": serializer.data
        }, status=status.HTTP_200_OK)

    
    
class CourseView(APIView):
    # 랜덤 여행 코스 조회
    @swagger_auto_schema(
        operation_summary="랜덤 여행 코스 조회",
        operation_description="랜덤 여행 코스를 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'course_id', 
                openapi.IN_QUERY, 
                description="course_id", 
                type=openapi.TYPE_INTEGER,
                example=20,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="랜덤 여행 코스 조회",
                examples={
                    "application/json": {
                        "message": "랜덤 여행 코스를 조회합니다.",
                        "result": {
                            "course_id": 20,
                            "tour_list": [
                                {
                                    "order": 1,
                                    "tour_id": 1912,
                                    "tour_name": "샘재골송이마을",
                                    "tour_address": "강원특별자치도 양양군 현북면 송이로 245-44",
                                    "tour_mapx": 128,
                                    "tour_mapy": 38
                                },
                                {
                                    "order": 2,
                                    "tour_id": 4029,
                                    "tour_name": "카페 달파도",
                                    "tour_address": "강원특별자치도 양양군 선사유적로 327",
                                    "tour_mapx": 128,
                                    "tour_mapy": 38
                                },
                                {
                                    "order": 3,
                                    "tour_id": 2009,
                                    "tour_name": "설온",
                                    "tour_address": "강원특별자치도 양양군 강현면 복골길201번길 58",
                                    "tour_mapx": 128,
                                    "tour_mapy": 38
                                },
                                {
                                    "order": 4,
                                    "tour_id": 621,
                                    "tour_name": "금풀애마을",
                                    "tour_address": "강원특별자치도 양양군 현북면 남대천로 1532",
                                    "tour_mapx": 128,
                                    "tour_mapy": 37
                                },
                                {
                                    "order": 5,
                                    "tour_id": 2751,
                                    "tour_name": "여운포리빵집",
                                    "tour_address": "강원특별자치도 양양군 선사유적로 73-13",
                                    "tour_mapx": 128,
                                    "tour_mapy": 38
                                }
                            ]
                        }
                    }
                }
            ),
        }
    )
    def get(self, request):
        course_id = request.GET.get('course_id')
        random_tour = RandomTour.objects.get(id=course_id)
        serializer = SaveRandomTourListSerializer(random_tour)
        return Response({
                "message": "랜덤 여행 코스를 조회합니다.",
                "result": serializer.data
                }, status=status.HTTP_200_OK)
    
    # 랜덤 여행 코스 저장
    @swagger_auto_schema(
        operation_summary="랜덤 여행 코스 저장",
        operation_description="랜덤 여행 코스를 저장합니다. tour_list의 경우, 리스트의 인덱스가 코스 내 여행지 순서(order)로 저장됩니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'tour_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), example=[1912, 4029, 2009, 621, 2751]),
            },
            required=['tour_list']
        ),
        responses={
            200: openapi.Response(
                description="랜덤 여행 코스 저장 성공",
                examples={
                    "application/json": {
                        "message": "랜덤 여행 결과를 저장합니다.",
                        "result": {
                            "course_id": 1,
                            "tour_list": [
                                {
                                    "order": 1,
                                    "tour_id": 1912,
                                    "tour_name": "샘재골송이마을",
                                    "tour_address": "강원특별자치도 양양군 현북면 송이로 245-44",
                                    "tour_mapx": 128,
                                    "tour_mapy": 38
                                },
                                {
                                    "order": 2,
                                    "tour_id": 4029,
                                    "tour_name": "카페 달파도",
                                    "tour_address": "강원특별자치도 양양군 선사유적로 327",
                                    "tour_mapx": 128,
                                    "tour_mapy": 38
                                },
                                {
                                    "order": 3,
                                    "tour_id": 2009,
                                    "tour_name": "설온",
                                    "tour_address": "강원특별자치도 양양군 강현면 복골길201번길 58",
                                    "tour_mapx": 128,
                                    "tour_mapy": 38
                                },
                                {
                                    "order": 4,
                                    "tour_id": 621,
                                    "tour_name": "금풀애마을",
                                    "tour_address": "강원특별자치도 양양군 현북면 남대천로 1532",
                                    "tour_mapx": 128,
                                    "tour_mapy": 37
                                },
                                {
                                    "order": 5,
                                    "tour_id": 2751,
                                    "tour_name": "여운포리빵집",
                                    "tour_address": "강원특별자치도 양양군 선사유적로 73-13",
                                    "tour_mapx": 128,
                                    "tour_mapy": 38
                                }
                            ]
                        }
                    }
                }
            ),
            400: openapi.Response(              description="저장 실패",
                examples={
                    "application/json": {
                        "message": "해당 Tour ID 5555는 존재하지 않습니다."
                    }
                }
            ),
        }
    )
    def post(self, request):
        tour_ids = request.data.get('tour_list', [])
        random_tour= RandomTour.objects.create(user=request.user)

        # 데이터 저장
        for order, tour_id in enumerate(tour_ids, start=1):
            try:
                tour = Tours.objects.get(id=tour_id)
            except Tours.DoesNotExist:
                return Response({"message": f"해당 Tour ID {tour_id}는 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            RandomTourOrder.objects.create(
                random_tour=random_tour,
                tour=tour,
                order=order
            )
        
        updated_random_tour = RandomTour.objects.get(id=random_tour.id)
        serializer = SaveRandomTourListSerializer(updated_random_tour)

        return Response({
                "message": "랜덤 여행 코스 결과를 저장합니다.",
                "result": serializer.data
                }, status=status.HTTP_200_OK)
    
    # 랜덤 여행 코스 수정
    @swagger_auto_schema(
        operation_summary="랜덤 여행 코스 수정",
        operation_description="랜덤 여행 코스를 수정합니다. tour_list의 경우, 리스트의 인덱스가 코스 내 여행지 순서(order)로 저장됩니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                'tour_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER), example=[3, 2, 1]),
            },
            required=['course_id', 'tour_list']
        ),
        responses={
            200: openapi.Response(
                description="랜덤 여행 코스 수정 성공",
                examples={
                    "application/json": {
                        "message": "랜덤 여행 코스를 수정합니다.",
                        "result": {
                            "course_id": 1,
                            "tour_list": [
                                {
                                    "order": 1,
                                    "tour_id": 3,
                                    "tour_name": "가곡유황온천&스파",
                                    "tour_address": "강원특별자치도 삼척시 가곡면 탕곡리",
                                    "tour_mapx": 129,
                                    "tour_mapy": 37
                                },
                                {
                                    "order": 2,
                                    "tour_id": 2,
                                    "tour_name": "가곡국민여가캠핑장",
                                    "tour_address": "강원특별자치도 삼척시 가곡면 탕곡리",
                                    "tour_mapx": 129,
                                    "tour_mapy": 37
                                },
                                {
                                    "order": 3,
                                    "tour_id": 1,
                                    "tour_name": "가고파부치기",
                                    "tour_address": "강원특별자치도 평창군 평창읍 평창시장2길 14",
                                    "tour_mapx": 128,
                                    "tour_mapy": 37
                                }
                            ]
                        }
                    }
                }
            ),
            400: openapi.Response(              description="수정 실패",
                examples={
                    "application/json": {
                        "message": "해당 Tour ID 5555는 존재하지 않습니다."
                    }
                }
            ),
            404: openapi.Response(
                description="조회 실패 - course_id 잘못됨",
            ),
        }
    )
    def put(self, request):
        tour_ids = request.data.get('tour_list')
        course_id = request.data.get('course_id')
        random_tour = get_object_or_404(RandomTour, id=course_id, user=request.user)

        # 기존 데이터 삭제
        RandomTourOrder.objects.filter(random_tour=random_tour).delete()

        # 데이터 저장
        for order, tour_id in enumerate(tour_ids, start=1):
            try:
                tour = Tours.objects.get(id=tour_id)
            except Tours.DoesNotExist:
                return Response({"message": f"해당 Tour ID {tour_id}는 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            RandomTourOrder.objects.create(
                random_tour=random_tour,
                tour=tour,
                order=order
            )
        
        updated_random_tour = RandomTour.objects.get(id=random_tour.id)
        serializer = SaveRandomTourListSerializer(updated_random_tour)

        return Response({
                "message": "랜덤 여행 코스를 수정합니다.",
                "result": serializer.data
                }, status=status.HTTP_200_OK)

class CourseListView(APIView):
    
    # 유저의 코스 목록 조회
    @swagger_auto_schema(
        operation_summary="유저의 랜덤 여행 코스 목록 조회",
        operation_description="유저의 랜덤 여행 코스 목록을 조회합니다.",
        responses={
            200: openapi.Response(
                description="랜덤 여행 코스 목록 조회",
                examples={
                    "application/json": {
                        "message": "랜덤 여행 코스 목록을 조회합니다.",
                        "result": {
                            "course_count": 2,
                            "course_list": [
                                {
                                    "course_id": 1,
                                    "created_at": "2024-09-16T19:30:11.176314Z"
                                },
                                {
                                    "course_id": 2,
                                    "created_at": "2024-09-16T19:30:11.176314Z"
                                },
                            ]
                        }
                    }
                }
            ),
            204: openapi.Response(
                description="랜덤 여행 코스 목록 조회",
                examples={
                    "application/json": {
                        "message": "조회된 결과가 없습니다."
                    }
                }
            ),
        }
    )
    def get(self, request):
        user = request.user
        random_tour = RandomTour.objects.filter(user=user)
        if not random_tour:
            return Response({
                "message": "조회된 결과가 없습니다.",
                }, status=status.HTTP_204_NO_CONTENT)
        
        serializer = RandomTourSerializer(random_tour, many=True)
        return Response({
                "message": "랜덤 여행 코스 목록을 조회합니다.",
                "result": {
                    "course_count": random_tour.count(),
                    "course_list": serializer.data,
                }
                }, status=status.HTTP_200_OK)