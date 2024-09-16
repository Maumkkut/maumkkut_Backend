# views.py

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from board.models import Post, Comment
from .serializers import UserPostSerializer, UserCommentSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Sum

class TenResultsSetPagination(PageNumberPagination):
    page_size = 10  # 페이지당 10개 항목

    def get_paginated_response(self, data):
        return Response({
            'total_count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

post_response_example = {
    'total_count': 2,
    'next': None,
    'previous': None,
    'results': [
        {
            'id': 1,
            'title': '최근 작성한 게시글',
            'content': '게시글 내용',
            'created_at': '5분 전',
            'board_type': 'free',
        },
        {
            'id': 2,
            'title': '어제 작성한 게시글',
            'content': '게시글 내용',
            'created_at': '1일 전',
            'board_type': 'free',
        }
    ]
}

comment_response_example = {
    'total_count': 2,
    'next': None,
    'previous': None,
    'results': [
        {
            'id': 1,
            'content': '최근 작성한 댓글',
            'post_title': '관련 게시글 제목',
            'created_at': '2시간 전',
        },
        {
            'id': 2,
            'content': '지난주에 작성한 댓글',
            'post_title': '관련 게시글 제목',
            'created_at': '1일 전',
        }
    ]
}

post_like_response_example = {
    'total_count': 1,
    'next': None,
    'previous': None,
    'results': [
        {
            'id': 1,
            'title': '좋아요한 게시글 제목',
            'content': '게시글 내용',
            'created_at': '5분 전',
            'board_type': 'free',
        }
    ]
}

@swagger_auto_schema(
    method='get',
    operation_summary="현재 사용자가 작성한 게시글 목록 조회",
    responses={
        200: openapi.Response(
            '성공',
            UserPostSerializer(many=True),
            examples={"application/json": post_response_example}
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_post_list(request):
    user = request.user
    posts = Post.objects.filter(author=user).order_by('-created_at')
    paginator = TenResultsSetPagination()
    result_page = paginator.paginate_queryset(posts, request)
    serializer = UserPostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@swagger_auto_schema(
    method='get',
    operation_summary="현재 사용자가 작성한 댓글 목록 조회",
    responses={
        200: openapi.Response(
            '성공',
            UserCommentSerializer(many=True),
            examples={"application/json": comment_response_example}
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_comment_list(request):
    user = request.user
    comments = Comment.objects.filter(author=user).order_by('-created_at')
    paginator = TenResultsSetPagination()
    result_page = paginator.paginate_queryset(comments, request)
    serializer = UserCommentSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@swagger_auto_schema(
    method='get',
    operation_summary="현재 사용자가 작성한 게시글 및 댓글 수와 받은 좋아요 수 조회",
    responses={
        200: openapi.Response(
            '성공',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'username': openapi.Schema(type=openapi.TYPE_STRING, description='사용자 이름'),
                    'post_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='게시글 수'),
                    'comment_count': openapi.Schema(type=openapi.TYPE_INTEGER, description='댓글 수'),
                    'total_likes': openapi.Schema(type=openapi.TYPE_INTEGER, description='받은 좋아요 수'),
                }
            ),
            examples={
                "application/json": {
                    "username": "example_user",
                    "post_count": 5,
                    "comment_count": 10,
                    "total_likes": 50
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_content_count(request):
    user = request.user
    post_count = Post.objects.filter(author=user).count()
    comment_count = Comment.objects.filter(author=user).count()
    total_likes = Post.objects.filter(author=user).annotate(num_likes=Count('liked_users')).aggregate(total_likes=Sum('num_likes'))['total_likes'] or 0
    
    return Response({
        'username': user.username,
        'post_count': post_count,
        'comment_count': comment_count,
        'total_likes': total_likes,
    }, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_summary="현재 사용자가 좋아요한 게시글 목록 조회",
    responses={
        200: openapi.Response(
            '성공',
            UserPostSerializer(many=True),
            examples={"application/json": post_like_response_example}
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_liked_posts(request):
    user = request.user
    posts = user.liked_posts.all().order_by('-created_at')
    paginator = TenResultsSetPagination()
    result_page = paginator.paginate_queryset(posts, request)
    serializer = UserPostSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)
