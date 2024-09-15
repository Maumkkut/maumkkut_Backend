from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Group
from .serializers import GroupSerializer, GroupListSerializer
from django.contrib.auth import get_user_model
import json
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# 그룹 생성 및 조회
class GroupView(APIView):
    
    @swagger_auto_schema(
        operation_summary="그룹 조회",
        operation_description="그룹 id로 그룹 상세를 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'group_id', 
                openapi.IN_QUERY, 
                description="group_id", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="group 조회",
                examples={
                    "application/json": {
                        "message": "그룹을 조회합니다.",
                        "result": {
                            "id": 1,
                            "name": "test2",
                            "members": [
                                3,
                                4
                            ],
                            "leader": 1,
                            "region": "강릉",
                            "start_date": "2000-01-01",
                            "end_date": "2000-01-02"
                        },
                    }
                }
            ),
            400: openapi.Response(
                description="group id가 null값인 경우",
                examples={
                    "application/json": {
                        "error": "group id는 null 일 수 없습니다."
                }
                }
            ),
            404: openapi.Response(
                description="group id가 존재하지 않을 경우",
                examples={
                    "application/json": {
                        "error": "존재하지 않는 그룹입니다."
                }
                }
            )
        }
    )
    def get(self, request):
        group_id = request.query_params.get('group_id')
        
        if not group_id:
            return Response({"error": "group id는 null 일 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "존재하지 않는 그룹입니다."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GroupSerializer(group)
        return Response({
                            "message": "그룹을 조회하였습니다",
                            "result":serializer.data
                        }, 
                        status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="그룹 생성",
        operation_description="그룹을 생성합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'leader': openapi.Schema(type=openapi.TYPE_INTEGER),
                'members': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'region': openapi.Schema(type=openapi.TYPE_STRING),
                'start_date': openapi.Schema(type=openapi.FORMAT_DATE),
                'end_date': openapi.Schema(type=openapi.FORMAT_DATE),
            },
            required=['leader', 'members', 'name', 'region', 'start_date', 'end_date']
        ),
        responses={
            201: openapi.Response(
                description="group 생성",
                examples={
                    "application/json": {
                        "message": "그룹을 생성합니다.",
                        "result": {
                            "id": 1,
                            "name": "test",
                            "members": [
                                3,
                                4,
                                5
                            ],
                            "leader": 1,
                            "region": "강릉",
                            "start_date": "2000-01-01",
                            "end_date": "2000-01-02"
                        },
                    }
                }
            ),
            400: openapi.Response(
                description="조회 실패",
                examples={
                    "application/json": {
                        "error": "group id는 null 일 수 없습니다."
                }
                }
            ),
        }
    )
    def post(self, request):
        # print(request.data)
        User = get_user_model()
        name = request.data.get('name')
        leader_id = request.data.get('leader')
        member_ids = request.data.get('members', [])
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        region = request.data.get('region')
        try:
            member_ids = json.loads(member_ids)
        except json.JSONDecodeError:
            return Response({"error": "포맷 에러"}, status=status.HTTP_400_BAD_REQUEST)

        leader = User.objects.get(id=leader_id)
        members = User.objects.filter(id__in=member_ids)

        # print(request.data)

        data = {
            'name': name,
            'leader': leader.id,  # 리더의 ID 전달
            'members': list(members.values_list('id', flat=True)), # 멤버 ID 리스트 전달
            'start_date': start_date,
            'end_date': end_date,
            'region': region,
        }

        serializer = GroupSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "mesasge": "그룹을 생성합니다.",
                "result": serializer.data
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# 나의 그룹 조회
class UserGroupView(APIView):

    @swagger_auto_schema(
        operation_summary="나의 그룹 조회",
        operation_description="나의 그룹 리스트를 조회합니다.",
        responses={
            200: openapi.Response(
                description="나의 group 조회",
                examples={
                    "application/json": {
                    "message": "나의 그룹을 조회합니다",
                    "result": [
                        {
                            "id": 1,
                            "name": "그룹1",
                            "start_date": "2000-01-01",
                            "end_date": "2000-01-02",
                            "region": "강릉"
                        },
                        {
                            "id": 2,
                            "name": "그룹2",
                            "start_date": "2000-01-01",
                            "end_date": "2000-01-02",
                            "region": "양양"
                        }
                    ]
                }
                }
            ),
            204: openapi.Response(
                description="group이 존재하지 않는 경우",
                examples={
                    "application/json": {
                        "error": "그룹이 존재하지 않습니다."
                }
                }
            ),
        }
    )
    def get(self, request):
        user = request.user
        groups = Group.get_groups_for_user(user.id)
        if groups:
            # 그룹이 존재할 경우
            print(groups)
            serializer = GroupListSerializer(groups, many=True)
            return Response({
                "message": "나의 그룹을 조회합니다",
                "result": serializer.data
                }, status=status.HTTP_200_OK)
            
        # 그룹이 존재하지 않을 경우
        return Response({"error": "그룹이 존재하지 않습니다."}, status=status.HTTP_204_NO_CONTENT)