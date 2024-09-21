from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Group
from .serializers import GroupSerializer, GroupListSerializer, GroupTourListSerializer, LikeDislikeSerializer, LikeTourListSerializer, GroupLikeTourListSerializer
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from createDB.models import GroupInfo, Tours
from createDB.DataProcessing.GroupSimilarityCourses import recommend_similar_group
from .models import GroupTourList, GroupTourOrder, LikeDislike, Tours

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
                description="생성 실패",
                examples={
                    "application/json": {
                        "error": "group id는 null 일 수 없습니다."
                }
                }
            ),
        }
    )
    def post(self, request):
        User = get_user_model()
        name = request.data.get('name')
        leader_id = request.data.get('leader')
        member_ids = request.data.get('members', [])
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        region = request.data.get('region')

        leader = User.objects.get(id=leader_id)
        members = User.objects.filter(id__in=member_ids)
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
            serializer = GroupListSerializer(groups, many=True)
            return Response({
                "message": "나의 그룹을 조회합니다",
                "result": serializer.data
                }, status=status.HTTP_200_OK)
            
        # 그룹이 존재하지 않을 경우
        return Response({"error": "그룹이 존재하지 않습니다."}, status=status.HTTP_204_NO_CONTENT)
    

# 그룹 유사도 기반 여행 리스트 추천
class RecommendGroupTourListView(APIView):

    @swagger_auto_schema(
        operation_summary="단체 여행지 추천",
        operation_description="유사도 기반 단체의 여행지 리스트를 추천받습니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'group_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'region': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['group_id', 'region']
        ),
        responses={
            200: openapi.Response(
                description="단체 여행지 추천",
                examples={
                    "application/json": {
                        "message": "추천된 단체 여행지 리스트입니다.",
                        "result": {
                            "route_id": 23,
                            "route_name": "route19",
                            "lodge": "lodge19",
                            "route_area": 1,
                            "tour_startdate": "2024-08-17T00:00:00Z",
                            "tour_enddate": "2024-08-18T00:00:00Z",
                            "group_id": 2,
                            "tour_info_list": [
                                {
                                    "tour_id": 4700,
                                    "title": "해피아워크루즈",
                                    "addr1": "강원특별자치도 강릉시 주문진읍 해안로 1730",
                                    "mapx": 128.828660257,
                                    "mapy": 37.8895791714
                                },
                                {
                                    "tour_id": 74,
                                    "title": "강릉 경포해수욕장",
                                    "addr1": "강원특별자치도 강릉시 창해로 514",
                                    "mapx": 128.9074446419,
                                    "mapy": 37.805729308
                                },
                                {
                                    "tour_id": 1757,
                                    "title": "사천진해변(사천뒷불해수욕장)",
                                    "addr1": "강원특별자치도 강릉시 사천면 진리해변길 111",
                                    "mapx": 128.8753492114,
                                    "mapy": 37.8412245725
                                },
                            ]
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="조회실패",
            ),
        }
    )
    def post(self, request):
        group_id = request.data.get('group_id')
        region = request.data.get('region')

        group = get_object_or_404(Group, id=group_id)
        people_num = len(group.get_members_with_leader())
        group_name = group.name
        group_info, created = GroupInfo.objects.get_or_create(
            group=group,
            defaults={
                'people_num': people_num,
                'group_name': group_name,
            }
        )
        if not created:
            group_info.people_num = people_num
            group_info.group_name = group_name
            group_info.save()

        result = recommend_similar_group(group, group_info.id, region)
        tour_info_list = result.get('tour_info_list', [])
        tour_ids = [tour['tour_id'] for tour in tour_info_list]
        
        group_tour_list, created = GroupTourList.objects.get_or_create(group=group)

        for index, tour_id in enumerate(tour_ids):
            tour = get_object_or_404(Tours, id=tour_id)
            group_tour_order, created = GroupTourOrder.objects.get_or_create(
                group_tour_list=group_tour_list, 
                tour=tour,
                defaults={'order': index + 1}
            )
            if not created:
                group_tour_order.order = index + 1
                group_tour_order.save()

        return Response({
            "message": "추천된 단체 여행지 리스트입니다.",
            "result": result},
            status=status.HTTP_200_OK)

# 단체 여행지 리스트
class GroupTourListView(APIView):

    @swagger_auto_schema(
        operation_summary="단체 여행지 리스트 조회",
        operation_description="단체 여행지 리스트를 조회합니다.",
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
                description="단체 여행지 리스트 조회",
                examples={
                    "application/json": {
                        "message": "단체 여행지 리스트를 조회합니다.",
                        "result": [
                            {
                                "group": 1,
                                "tour_list": [
                                    {
                                        "order": 1,
                                        "tour": {
                                            "id": 4700,
                                            "title": "해피아워크루즈",
                                            "addr1": "강원특별자치도 강릉시 주문진읍 해안로 1730",
                                            "mapx": 128.828660257,
                                            "mapy": 37.8895791714
                                        }
                                    },
                                    {
                                        "order": 2,
                                        "tour": {
                                            "id": 74,
                                            "title": "강릉 경포해수욕장",
                                            "addr1": "강원특별자치도 강릉시 창해로 514",
                                            "mapx": 128.9074446419,
                                            "mapy": 37.805729308
                                        }
                                    },
                                    {
                                        "order": 3,
                                        "tour": {
                                            "id": 1757,
                                            "title": "사천진해변(사천뒷불해수욕장)",
                                            "addr1": "강원특별자치도 강릉시 사천면 진리해변길 111",
                                            "mapx": 128.8753492114,
                                            "mapy": 37.8412245725
                                        }
                                    },
                                    {
                                        "order": 4,
                                        "tour": {
                                            "id": 2074,
                                            "title": "소돌해수욕장",
                                            "addr1": "강원특별자치도 강릉시 주문진읍 해안로 1993",
                                            "mapx": 128.8272654209,
                                            "mapy": 37.9062383246
                                        }
                                    },
                                ]
                            }
                        ]
                    }
                }
            ),
            404: openapi.Response(
                description="단체 여행지 리스트가 존재하지 않을 경우",
                examples={
                    "application/json": {
                        "message": "단체 여행지 리스트가 존재하지 않습니다."
                    }
                }
            )
        }
    )
    def get(self, request):
        group_id = request.GET.get('group_id')
        group_tour_list = GroupTourList.objects.filter(group_id=group_id)

        if not group_tour_list.exists():
            return Response({"message": "단체 여행지 리스트가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = GroupTourListSerializer(group_tour_list, many=True)
        return Response({"message": "단체 여행지 리스트를 조회합니다.",
            "result": serializer.data}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="단체 여행지 리스트 수정",
        operation_description="단체 여행지 리스트를 수정합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'group_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'tour_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_INTEGER)),
            },
            required=['group_id', 'tour_list']
        ),
        responses={
            200: openapi.Response(
                description="단체 여행지 리스트 수정",
                examples={
                    "application/json": {
                        "message": "단체 여행지 리스트가 업데이트되었습니다.",
                        "result": {
                            "group": 1,
                            "tour_list": [
                                {
                                    "order": 0,
                                    "tour": {
                                        "id": 1,
                                        "title": "가고파부치기",
                                        "addr1": "강원특별자치도 평창군 평창읍 평창시장2길 14",
                                        "mapx": 128.3949124655,
                                        "mapy": 37.3664313199
                                    }
                                },
                                {
                                    "order": 1,
                                    "tour": {
                                        "id": 4,
                                        "title": "가도 가도 또 가고 싶은 여행지의 스테디셀러",
                                        "addr1": "",
                                        "mapx": 128.6003708453,
                                        "mapy": 38.2133149015
                                    }
                                },
                                {
                                    "order": 2,
                                    "tour": {
                                        "id": 5,
                                        "title": "가람리조트",
                                        "addr1": "강원특별자치도 홍천군 두촌면 부채들길 29",
                                        "mapx": 128.018374124,
                                        "mapy": 37.8364809027
                                    }
                                }
                            ]
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="여행지가 존재하지 않을 경우",
                examples={
                    "application/json": {
                        "message": "해당 Tour ID 5555는 존재하지 않습니다."
                    }
                }
            ),
            404: openapi.Response(
                description="단체 여행 리스트가 존재하지 않을 경우",
                examples={
                    "application/json": {
                        "message": "단체 여행 리스트가 존재하지 않습니다."
                    }
                }
            )
        }
    )
    def put(self, request):
        group_id = request.data.get('group_id')
        tour_ids = request.data.get('tour_list', [])
        group_tour_list = GroupTourList.objects.get(group_id=group_id)
        if not group_tour_list:
            return Response({"message": "단체 여행 리스트가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 기존 데이터 삭제
        GroupTourOrder.objects.filter(group_tour_list=group_tour_list).delete()

        # 새로운 데이터 저장
        for order, tour_id in enumerate(tour_ids, start=1):
            try:
                tour = Tours.objects.get(id=tour_id)
            except Tours.DoesNotExist:
                return Response({"message": f"해당 Tour ID {tour_id}는 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            GroupTourOrder.objects.create(
                group_tour_list=group_tour_list,
                tour=tour,
                order=order
            )

        # 인스턴스 가져오기
        updated_group_tour_list = GroupTourList.objects.get(id=group_tour_list.id)  
        serializer = GroupTourListSerializer(updated_group_tour_list)

        return Response({
            "message": "단체 여행지 리스트가 업데이트되었습니다.",
            "result": serializer.data
        }, status=status.HTTP_200_OK)


class LikeDislikeView(APIView):

    @swagger_auto_schema(
        operation_summary="여행지 좋아요/싫어요 조회",
        operation_description="여행지의 좋아요/싫어요를 조회합니다.",
        manual_parameters=[
            openapi.Parameter(
                'tour_id', 
                openapi.IN_QUERY, 
                description="tour_id", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="조회 성공",
                examples={
                    "application/json": {
                    "message": "좋아요/싫어요 상태를 조회합니다.",
                    "result": {
                        "user": 1,
                        "tour": 1,
                        "is_liked": "true",
                        "is_disliked": "false"
                    }
                }
                }
            ),
            404: openapi.Response(
                description="조회 실패",
                examples={
                    "application/json": {
                        "message": "좋아요/싫어요 기록이 없습니다."
                }
                }
            )
        }
    )
    def get(self, request):
        # 단일 여행지에 대한 유저의 좋아요/싫어요 상태를 조회
        user = request.user
        tour_id = request.query_params.get('tour_id')
        tour = get_object_or_404(Tours, id=tour_id)
        like_dislike = LikeDislike.objects.filter(user=user, tour=tour).first()

        if like_dislike:
            serializer = LikeDislikeSerializer(like_dislike)
            return Response({"message": "좋아요/싫어요 상태를 조회합니다.", "result": serializer.data}, status=status.HTTP_200_OK)
        return Response({"message": "좋아요/싫어요 기록이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_summary="여행지 좋아요/싫어요 생성 및 수정",
        operation_description="여행지 좋아요/싫어요를 업데이트합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'tour_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'is_liked': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'is_disliked': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            },
            required=['tour_id', 'is_liked', 'is_disliked']
        ),
        responses={
            200: openapi.Response(
                description="좋아요/싫어요 생성 및 수정",
                examples={
                    "application/json": {
                        "message": "좋아요/싫어요 상태가 저장/업데이트되었습니다.",
                        "result": {
                            "user": 1,
                            "tour": 1,
                            "is_liked": "true",
                            "is_disliked": "false"
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="좋아요와 싫어요 둘 다 true일 경우",
                examples={
                    "application/json": {
                        "message": "유효하지 않은 데이터입니다.",
                        "errors": {
                            "non_field_errors": [
                                "좋아요와 싫어요를 동시에 선택할 수 없습니다."
                            ]
                        }
                    }
                }
            ),
        }
    )
    def put(self, request):
        # 유저가 특정 투어에 대해 좋아요 또는 싫어요를 업데이트
        user = request.user
        tour_id = request.data.get('tour_id')
        tour = get_object_or_404(Tours, id=tour_id)
        data = request.data

        # 기존의 좋아요/싫어요 기록 가져오기 (없으면 생성)
        like_dislike, created = LikeDislike.objects.get_or_create(user=user, tour=tour)

        # 좋아요/싫어요 상태 업데이트
        serializer = LikeDislikeSerializer(like_dislike, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            if created:
                message = "좋아요/싫어요 상태가 저장되었습니다."
            else:
                message = "좋아요/싫어요 상태가 업데이트되었습니다."
            return Response({"message": message, "result": serializer.data}, status=status.HTTP_200_OK)

        return Response({"message": "유효하지 않은 데이터입니다.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LikeTourListView(APIView):

    @swagger_auto_schema(
        operation_summary="유저의 여행지 리스트 좋아요/싫어요 조회",
        operation_description="여행지 리스트의 좋아요/싫어요를 조회합니다.",
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
                description="조회 성공",
                examples={
                    "application/json": {
                        "message": "유저의 해당 단체 여행지 리스트의 좋아요/싫어요를 조회합니다.",
                        "result": [
                            {
                                "group": 1,
                                "tour_list": [
                                    {
                                        "tour_id": 2,
                                        "tour_name": "가곡국민여가캠핑장",
                                        "is_liked": 'true',
                                        "is_disliked": 'false'
                                    },
                                    {
                                        "tour_id": 4,
                                        "tour_name": "가도 가도 또 가고 싶은 여행지의 스테디셀러",
                                        "is_liked": 'false',
                                        "is_disliked": 'false'
                                    },
                                    {
                                        "tour_id": 5,
                                        "tour_name": "가람리조트",
                                        "is_liked": 'false',
                                        "is_disliked": 'false'
                                    }
                                ]
                            }
                        ]
                    }
                }
            ),
            404: openapi.Response(
                description="조회 실패",
                examples={
                    "application/json": {
                        "message": "단체 여행지 리스트가 존재하지 않습니다."
                    }
                }
            )
        }
    )
    def get(self, request):
        # 그룹의 여행지에 대한 유저의 좋아요/싫어요 상태를 조회
        group_id = request.GET.get('group_id')
        group_tour_list = GroupTourList.objects.filter(group_id=group_id)

        if not group_tour_list.exists():
            return Response({"message": "단체 여행지 리스트가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = LikeTourListSerializer(group_tour_list, context={'request': request}, many=True)
        return Response({"message": "유저의 해당 단체 여행지 리스트의 좋아요/싫어요를 조회합니다.",
            "result": serializer.data}, status=status.HTTP_200_OK)

class GroupLikeTourListView(APIView):
    
    @swagger_auto_schema(
        operation_summary="단체 여행지 리스트 좋아요/싫어요 카운트 및 해당 멤버 조회",
        operation_description="여행지 리스트의 좋아요/싫어요 카운트 및 해당 멤버를 조회합니다.",
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
                description="조회 성공",
                examples={
                    "application/json": {
                        "message": "단체의 좋아요/싫어요 카운트 및 해당 멤버를 조회합니다.",
                        "result": [
                            {
                                "group": 11,
                                "tour_list": [
                                    {
                                        "tour_id": 4156,
                                        "tour_name": "키즈몬 강릉점",
                                        "like_count": 1,
                                        "dislike_count": 1,
                                        "like_members": [
                                            "test"
                                        ],
                                        "dislike_members": [
                                            "test2"
                                        ]
                                    },
                                    {
                                        "tour_id": 3889,
                                        "tour_name": "초당젤라또 도깨비점",
                                        "like_count": 0,
                                        "dislike_count": 2,
                                        "like_members": [],
                                        "dislike_members": [
                                            "test",
                                            "test2"
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            ),
            204: openapi.Response(
                description="조회 실패",
                examples={
                    "application/json": {
                        "message": "단체 여행지 리스트가 존재하지 않습니다."
                    }
                }
            ),
            404: openapi.Response(
                description="조회 실패",
                examples={
                    "application/json": {
                        "message": "해당 그룹을 찾을 수 없습니다."
                    }
                }
            )
        }
    )
    def get(self, request):
        # 그룹의 여행지에 대한 그룹 멤버의 좋아요/싫어요 상태를 조회
        group_id = request.GET.get('group_id')
        group = Group.objects.get(id=group_id)
        if not group:
            return Response({
                "message": "해당 그룹을 찾을 수 없습니다."
                }, status=status.HTTP_404_NOT_FOUND)
        group_tour_list = GroupTourList.objects.filter(group_id=group_id)

        if not group_tour_list.exists():
            return Response({
                "message": "단체 여행지 리스트가 존재하지 않습니다."
                }, status=status.HTTP_204_NO_CONTENT)
        
        serializer = GroupLikeTourListSerializer(group_tour_list, context={'request': request}, many=True)
        return Response({"message": "단체 여행지의 좋아요/싫어요 및 해당 멤버를 조회합니다.",
            "result": serializer.data}, status=status.HTTP_200_OK)

class CheckGroupName(APIView):
    @swagger_auto_schema(
        operation_summary="그룹 이름 중복체크",
        operation_description="그룹 이름의 중복체크",
        manual_parameters=[
            openapi.Parameter(
                'group_name', 
                openapi.IN_QUERY, 
                description="group_name", 
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="group name 사용 가능",
                examples={
                    "application/json": {
                        "message":
                        "사용할 수 있는 group name 입니다.",
                        "result": {
                            "group_name": "group1"
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="조회 실패",
                examples={
                    "application/json": {
                        "message": "group name은 null일 수 없습니다."
                    }
                }
            ),
            409: openapi.Response(
                description="group name 사용 불가",
                examples={
                    "application/json": {
                        "message": "존재하는 group name 입니다."
                    }
                }
            )
        }
    )
    def get(self, request):
        group_name = request.GET.get('group_name')
        if group_name:
            
            if not Group.objects.filter(name=group_name).exists():
                # group name 없음
                return Response(
                    {
                        "message":
                        "사용할 수 있는 group name 입니다.",
                        "result": {
                            "group_name": group_name
                        }
                    }
                )
            
            return Response({
                "message": "존재하는 group name 입니다."
            }, status=status.HTTP_409_CONFLICT)
        return Response(
                {
                    "message": "group name은 null일 수 없습니다.",
                },
                status=status.HTTP_400_BAD_REQUEST
                )
        

