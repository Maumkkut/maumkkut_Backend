from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from createDB.DataProcessing.TravelCharacter import recommend_character
from createDB.models import User_info
from .serializers import TestResultSerializer, TestListSerializer
from .models import TravelTest
# Create your views here.
# 유저의 여행 결과 저장 / 삭제
# 테스트할때마다 userInfo update 필수
class TravelTestView(APIView):

    # 여행 취향 테스트 조회
    @swagger_auto_schema(
        operation_summary="여행 취향 테스트 조회",
        operation_description="유저의 여행 취향 테스트를 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'test_id', 
                openapi.IN_QUERY, 
                description="test_id", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="조회 성공",
                examples={
                    "application/json": {
                        "mesasge": "여행 취향 테스트를 조회합니다.",
                        "result": [
                            {
                                "character_type": "미식가형 송이",
                                "character_description": "맛집 탐방과 음식을 즐기는 여행을 선호",
                                "recommend_place": "춘천",
                                "recommend_reason": "맛집 탐방과 음식을 즐기는 '황태' 유형에게 춘천은 다양한 맛집이 있어 미식 여행을 즐기기에 적합한 곳입니다.",
                                "best_match": "관람형 곤드레",
                                "match_reason": "맛집 탐방과 문화 관람을 함께 즐길 수 있는 두 유형은 여행 중 자연스럽게 서로의 취향을 반영한 일정을 만들 수 있어 서로에게 긍정적인 영향을 줍니다."
                            }
                        ]
                    }
                }
            ),
            204: openapi.Response(
                description="조회 실패",
                examples={
                    "application/json": {
                        "message": "여행 취향 테스트 결과가 없습니다.",
                    }
                }
            ),
        }
    )
    def get(self, request):
        test_id = request.GET.get('test_id')
        travel_tests = TravelTest.objects.filter(id=test_id)
        
        if not travel_tests:
            return Response({
                "message": "잘못된 ID 입니다.",
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TestResultSerializer(travel_tests, many=True)
        return Response({
                "mesasge": "여행 취향 테스트를 조회합니다.",
                "result": serializer.data
                }, status=status.HTTP_200_OK)

    # 여행 결과 저장
    @swagger_auto_schema(
        operation_summary="여행 취향 테스트 결과 조회 및 저장",
        operation_description="여행 취향 테스트 결과 입니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'importance_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
            },
            required=['importance_list']
        ),
        responses={
            200: openapi.Response(
                description="테스트 결과 조회 성공",
                examples={
                    "application/json": {
                        "mesasge": "여행 취향 테스트 결과입니다.",
                        "result": {
                            "test_id": 1,
                            "character_type": "미식가형 송이",
                            "character_description": "맛집 탐방과 음식을 즐기는 여행을 선호",
                            "recommend_place": "춘천",
                            "recommend_reason": "맛집 탐방과 음식을 즐기는 '황태' 유형에게 춘천은 다양한 맛집이 있어 미식 여행을 즐기기에 적합한 곳입니다.",
                            "best_match": "관람형 곤드레",
                            "match_reason": "맛집 탐방과 문화 관람을 함께 즐길 수 있는 두 유형은 여행 중 자연스럽게 서로의 취향을 반영한 일정을 만들 수 있어 서로에게 긍정적인 영향을 줍니다."
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="조회 실패",
                examples={
                    "application/json": {
                        "message": "잘못된 결과값입니다."
                    }
                }
            ),
        }
    )
    def post(self, request):
        importance_list = request.data.get('importance_list')

        if not importance_list or len(importance_list) != 10:
            return Response({"message": "잘못된 결과값입니다. 중요도 리스트의 길이가 10인지 확인하세요."}, status=status.HTTP_400_BAD_REQUEST)
        
        character_info = recommend_character(importance_list)
        self.save_userinfo(request, importance_list, character_info)

        data = {
            'character_type': character_info[0], 'character_description': character_info[1], 
            'recommend_place': character_info[2], 'recommend_reason': character_info[3], 
            'best_match': character_info[4],
            'match_reason': character_info[5], 
        }
        serializer = TestResultSerializer(data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "mesasge": "여행 취향 테스트 결과입니다.",
                "result": serializer.data
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    # 여행 결과 삭제
    @swagger_auto_schema(
        operation_summary="여행 취향 테스트 삭제",
        operation_description="유저의 여행 취향 테스트 결과를 삭제합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'test_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['test_id']
        ),
        responses={
            204: openapi.Response(
                description="삭제 성공",
                examples={
                    "application/json": {
                        "message": "여행 취향 테스트 결과가 삭제되었습니다."
                    }
                }
            ),
            400: openapi.Response(
                description="삭제 실패",
                examples={
                    "application/json": {
                        "message": "ID가 제공되지 않았습니다."
                    }
                }
            ),
            404: openapi.Response(
                description="삭제 실패",
                examples={
                    "application/json": {
                        "message": "해당 테스트 결과를 찾을 수 없습니다."
                    }
                }
            )
        }
    )
    def delete(self, request):
        test_id = request.data.get('test_id')
        
        if not test_id:
            return Response({"message": "ID가 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            travel_test = TravelTest.objects.get(id=test_id, user=request.user)
            travel_test.delete()
            return Response({"message": "여행 취향 테스트 결과가 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        except TravelTest.DoesNotExist:
            return Response({"message": "해당 테스트 결과를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    # userinfo에 가장 최신의 테스트 결과 저장
    def save_userinfo(self, request, importance_list, character_info):
        user = request.user
        user_info, created = User_info.objects.get_or_create(user=user)
        user_info.user_type = character_info[0]
        user_info.user_healing = importance_list[0]
        user_info.user_relax = importance_list[1]
        user_info.user_nature = importance_list[2]
        user_info.user_exhibit = importance_list[3]
        user_info.user_food = importance_list[4]
        user_info.user_adventure = importance_list[5]
        user_info.user_people = importance_list[7]
        user_info.user_shopping = importance_list[8]
        user_info.user_photo = importance_list[9]
        user_info.save()

class TravelTestListView(APIView):
    # 여행 취향 테스트 목록 조회
    @swagger_auto_schema(
        operation_summary="여행 취향 테스트 목록 조회",
        operation_description="유저의 여행 취향 테스트 결과 목록을 조회합니다.",
        responses={
            200: openapi.Response(
                description="조회 성공",
                examples={
                    "application/json": {
                        "mesasge": "여행 취향 테스트 목록을 조회합니다.",
                        "result": [
                            {
                                "id": 2,
                                "character_type": "미식가형 송이",
                                "created_at": "2024-09-16T16:22:20.175429Z"
                            },
                            {
                                "id": 1,
                                "character_type": "미식가형 송이",
                                "created_at": "2024-09-16T16:14:11.199690Z"
                            }
                        ]
                    }
                }
            ),
            204: openapi.Response(
                description="조회 실패",
                examples={
                    "application/json": {
                        "message": "여행 취향 테스트 결과가 없습니다.",
                    }
                }
            ),
        }
    )
    def get(self, request):
        travel_tests = TravelTest.objects.filter(user=request.user).order_by('-created_at')
        if not travel_tests:
            return Response({
                "message": "여행 취향 테스트 결과가 없습니다.",
            }, status=status.HTTP_204_NO_CONTENT)
        
        serializer = TestListSerializer(travel_tests, many=True)
        return Response({
                "mesasge": "여행 취향 테스트 목록을 조회합니다.",
                "result": serializer.data
                }, status=status.HTTP_200_OK)