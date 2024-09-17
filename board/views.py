from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Post, Comment
from .serializers import CommentSerializer, PostDetailSerializer, PostListSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
import django_filters

class TenResultsSetPagination(PageNumberPagination):
    page_size = 10  # 페이지당 10개 항목

    def get_paginated_response(self, data):
        return Response({
            'total_count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

# 예시 데이터
post_example = {
    'title': '예시 제목',
    'content': '예시 내용',
}

comment_example = {
    'content': '예시 댓글 내용',
}

post_response_example = {
    'total_count': 1,
    'next': None,
    'previous': None,
    'results': [
        {
            'id': 1,
            'title': '예시 제목',
            'content': '예시 내용',
            'author': {'id': 1, 'username': 'example_user'},
            'board_type': 'free',
            'created_at': '2023-01-01T00:00:00Z',
            'comment_count': 1,
            'liked_users_count': 5
        }
    ]
}

comment_response_example = {
    'total_count': 1,
    'next': None,
    'previous': None,
    'results': [
        {
          "id": 1,
          "content": "예시 댓글 내용",
          "author_username": "string",
          "created_at": "2024-09-15T07:15:23.917615Z",
          "replies": [],
          "post_id": 1,
          "board_type": "travel"
        }
    ]
}

def get_board_posts(request, board_type):
    # 게시글을 최신순으로 정렬
    posts = Post.objects.filter(board_type=board_type).prefetch_related('comments').order_by('-created_at')
    paginator = TenResultsSetPagination()
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostListSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

def get_post_detail(request, pk, board_type):
    try:
        post = Post.objects.prefetch_related('comments').get(pk=pk, board_type=board_type)
    except Post.DoesNotExist:
        return Response({"error": "게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    serializer = PostDetailSerializer(post)
    return Response(serializer.data)

def get_comments_for_post(request, post_id):
    # 댓글을 최신순으로 정렬
    comments = Comment.objects.filter(post_id=post_id).order_by('-created_at')
    paginator = TenResultsSetPagination()
    result_page = paginator.paginate_queryset(comments, request)
    serializer = CommentSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

def handle_comment_detail(request, post_id, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, post_id=post_id)
    except Comment.DoesNotExist:
        return Response({"error": "댓글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post_id=post_id, parent_comment=comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def update_or_delete_comment(request, post_id, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, post_id=post_id)
    except Comment.DoesNotExist:
        return Response({"error": "댓글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        if comment.author != request.user:
            return Response({"error": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if comment.author != request.user:
            return Response({"error": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        comment.delete()
        return Response({"message": "댓글이 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

def get_recent_posts(request, days):
    date_from = timezone.now() - timedelta(days=days)
    posts = Post.objects.filter(created_at__gte=date_from).order_by('-created_at')
    paginator = TenResultsSetPagination()
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostListSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

def filter_posts(request, board_type):
    if board_type == "all":
        queryset = Post.objects.all()
    else:
        queryset = Post.objects.filter(board_type=board_type)
        

    # 기간(days) 필터링
    days = request.GET.get('days')
    if days:
        try:
            days = int(days)
            date_from = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=date_from)
        except ValueError:
            pass

    # 검색(search_type) 필터링
    search_type = request.GET.get('search_type')
    content = request.GET.get('content')
    if search_type and content:
        if search_type == 'title':
            queryset = queryset.filter(title__icontains=content)
        elif search_type == 'content':
            queryset = queryset.filter(content__icontains=content)
        elif search_type == 'author':
            queryset = queryset.filter(author__username__icontains=content)

    return queryset.order_by('-created_at')

@swagger_auto_schema(
    method='get',
    operation_summary="게시판 게시글 목록 조회 및 검색",
    operation_description="게시판의 게시글 목록을 가져옵니다. 'days', 'search_type', 'content' 파라미터로 검색이 가능합니다.",
    manual_parameters=[
        openapi.Parameter('days', openapi.IN_QUERY, description="조회할 기간 (일 단위)", type=openapi.TYPE_INTEGER),
        openapi.Parameter('search_type', openapi.IN_QUERY, description="검색 유형 (title, content, author)", type=openapi.TYPE_STRING),
        openapi.Parameter('content', openapi.IN_QUERY, description="검색 내용", type=openapi.TYPE_STRING),
    ],
    responses={200: openapi.Response('성공', PostListSerializer(many=True), examples={"application/json": [post_response_example]})}
)
@swagger_auto_schema(
    method='post',
    operation_summary="게시판 새 게시글 작성",
    operation_description="게시판에 새 게시글을 작성합니다",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING, description='제목'),
            'content': openapi.Schema(type=openapi.TYPE_STRING, description='내용'),
            'author': openapi.Schema(type=openapi.TYPE_INTEGER, description='작성자 ID'),
            'board_type': openapi.Schema(type=openapi.TYPE_STRING, description='게시판 타입')
        },
        example=post_example
    ),
    responses={201: openapi.Response('성공', PostDetailSerializer, examples={"application/json": post_response_example}), 400: '잘못된 요청'}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list(request, board_type):
    if request.method == 'GET':
        # 필터링된 게시글 가져오기
        posts = filter_posts(request, board_type)

        # 페이지네이션 처리
        paginator = TenResultsSetPagination()
        result_page = paginator.paginate_queryset(posts, request)
        serializer = PostListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    elif request.method == 'POST':
        # 관리자가 아니면 게시글 작성 불가
        if board_type == 'notice' and not request.user.is_admin():
            return Response({"error": "공지 작성 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PostDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, board_type=board_type)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    operation_summary="게시판 게시글 상세 조회",
    manual_parameters=[
        openapi.Parameter('board_type', openapi.IN_PATH, description="게시판 타입", type=openapi.TYPE_STRING),
        openapi.Parameter('pk', openapi.IN_PATH, description="게시글 ID", type=openapi.TYPE_INTEGER)
    ],
    operation_description="게시판의 특정 게시글 상세 정보를 가져옵니다",
    responses={200: openapi.Response('성공', PostDetailSerializer, examples={"application/json": post_response_example}), 404: '게시글을 찾을 수 없습니다'}
)
@swagger_auto_schema(
    method='put',
    operation_summary="게시판 게시글 수정",
    manual_parameters=[
        openapi.Parameter('board_type', openapi.IN_PATH, description="게시판 타입", type=openapi.TYPE_STRING),
        openapi.Parameter('pk', openapi.IN_PATH, description="게시글 ID", type=openapi.TYPE_INTEGER)
    ],
    operation_description="게시판의 특정 게시글을 수정합니다",
    request_body=PostDetailSerializer,
    responses={200: openapi.Response('성공', PostDetailSerializer, examples={"application/json": post_response_example}), 400: '잘못된 요청', 403: '수정 권한이 없습니다'}
)
@swagger_auto_schema(
    method='delete',
    operation_summary="게시판 게시글 삭제",
    manual_parameters=[
        openapi.Parameter('board_type', openapi.IN_PATH, description="게시판 타입", type=openapi.TYPE_STRING),
        openapi.Parameter('pk', openapi.IN_PATH, description="게시글 ID", type=openapi.TYPE_INTEGER)
    ],
    operation_description="게시판의 특정 게시글을 삭제합니다",
    responses={204: '게시글이 삭제되었습니다', 404: '게시글을 찾을 수 없습니다'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_operations(request, board_type, pk):
    try:
        post = Post.objects.get(pk=pk, board_type=board_type)
    except Post.DoesNotExist:
        return Response({"error": "게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PostDetailSerializer(post)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not request.user.is_admin():
            return Response({"error": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PostDetailSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.is_admin():
            return Response({"error": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        post.delete()
        return Response({"message": "게시글이 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='post',
    operation_summary="댓글 작성",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'content': openapi.Schema(type=openapi.TYPE_STRING, description='댓글 내용'),
        },
        example=comment_example
    ),
    responses={201: openapi.Response('성공', CommentSerializer, examples={"application/json": comment_response_example}), 400: '잘못된 요청'}
)
@swagger_auto_schema(
    method='get',
    operation_summary="댓글 목록 조회",
    manual_parameters=[
        openapi.Parameter('post_id', openapi.IN_PATH, description="게시글 ID", type=openapi.TYPE_INTEGER)
    ],
    operation_description="게시글에 대한 댓글 목록을 가져옵니다.",
    responses={200: openapi.Response('성공', CommentSerializer(many=True), examples={"application/json": [comment_response_example]})}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_list(request, post_id):
    if request.method == 'GET':
        return get_comments_for_post(request, post_id)
    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post_id=post_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    operation_summary="게시판 댓글 상세 조회",
    manual_parameters=[
        openapi.Parameter('post_id', openapi.IN_PATH, description="게시글 ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('comment_id', openapi.IN_PATH, description="댓글 ID", type=openapi.TYPE_INTEGER)
    ],
    operation_description="게시판의 특정 게시글에 대한 댓글 상세 내용을 가져옵니다",
    responses={200: openapi.Response('성공', CommentSerializer, examples={"application/json": comment_response_example}), 404: '댓글을 찾을 수 없습니다'}
)
@swagger_auto_schema(
    method='post',
    operation_summary="게시판 댓글에 답글 작성",
    manual_parameters=[
        openapi.Parameter('post_id', openapi.IN_PATH, description="게시글 ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('comment_id', openapi.IN_PATH, description="댓글 ID", type=openapi.TYPE_INTEGER)
    ],
    operation_description="게시판의 특정 게시글에 대한 댓글에 답글을 작성합니다",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'content': openapi.Schema(type=openapi.TYPE_STRING, description='댓글 내용'),
            'author': openapi.Schema(type=openapi.TYPE_INTEGER, description='작성자 ID'),
            'post': openapi.Schema(type=openapi.TYPE_INTEGER, description='게시글 ID')
        },
        example=comment_example
    ),
    responses={201: openapi.Response('성공', CommentSerializer, examples={"application/json": comment_response_example}), 400: '잘못된 요청'}
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_detail(request, post_id, comment_id):
    return handle_comment_detail(request, post_id, comment_id)

@swagger_auto_schema(
    method='put',
    operation_summary="게시판 댓글 수정",
    manual_parameters=[
        openapi.Parameter('post_id', openapi.IN_PATH, description="게시글 ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('comment_id', openapi.IN_PATH, description="댓글 ID", type=openapi.TYPE_INTEGER)
    ],
    operation_description="게시판의 특정 게시글에 대한 댓글을 수정합니다",
    request_body=CommentSerializer,
    responses={200: openapi.Response('성공', CommentSerializer, examples={"application/json": comment_response_example}), 400: '잘못된 요청', 403: '수정 권한이 없습니다'}
)
@swagger_auto_schema(
    method='delete',
    operation_summary="게시판 댓글 삭제",
    manual_parameters=[
        openapi.Parameter('post_id', openapi.IN_PATH, description="게시글 ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('comment_id', openapi.IN_PATH, description="댓글 ID", type=openapi.TYPE_INTEGER)
    ],
    operation_description="게시판의 특정 게시글에 대한 댓글을 삭제합니다",
    responses={204: '댓글이 삭제되었습니다', 403: '삭제 권한이 없습니다'}
)
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_operations(request, post_id, comment_id):
    return update_or_delete_comment(request, post_id, comment_id)

@swagger_auto_schema(
    method='post',
    operation_summary="게시글 또는 댓글 신고",
    manual_parameters=[
        openapi.Parameter('item_type', openapi.IN_PATH, description="아이템 타입 (post 또는 comment)", type=openapi.TYPE_STRING),
        openapi.Parameter('item_id', openapi.IN_PATH, description="아이템 ID", type=openapi.TYPE_INTEGER)
    ],
    operation_description="게시글 또는 댓글을 신고합니다",
    responses={
        200: openapi.Response('신고가 완료되었습니다', examples={"application/json": {"message": "신고가 완료되었습니다"}}),
        400: openapi.Response('잘못된 요청', examples={"application/json": {"error": "잘못된 요청입니다"}}),
        404: openapi.Response('아이템을 찾을 수 없습니다', examples={"application/json": {"error": "아이템을 찾을 수 없습니다"}})
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def report_item(request, item_type, item_id):
    user = request.user
    if item_type == 'post':
        try:
            item = Post.objects.get(id=item_id)
        except Post.DoesNotExist:
            return Response({'error': '게시글이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    elif item_type == 'comment':
        try:
            item = Comment.objects.get(id=item_id)
        except Comment.DoesNotExist:
            return Response({'error': '댓글이 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': '잘못된 타입입니다.'}, status=status.HTTP_400_BAD_REQUEST)

    if user in item.reported_by.all():
        return Response({'message': '이미 신고한 항목입니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    item.reported_by.add(user)
    item.save()
    return Response({'message': '신고가 완료되었습니다.'}, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='get',
    operation_summary="신고된 게시글 조회",
    operation_description="신고된 모든 게시글을 조회합니다",
    responses={200: openapi.Response('성공', PostListSerializer(many=True), examples={"application/json": [post_response_example]})}
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def reported_posts_list(request):
    posts = Post.objects.filter(reported_by__isnull=False).distinct()
    paginator = TenResultsSetPagination()
    result_page = paginator.paginate_queryset(posts, request)
    serializer = PostListSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@swagger_auto_schema(
    method='get',
    operation_summary="신고된 게시글 상세 조회",
    operation_description="특정 ID의 신고된 게시글을 조회합니다",
    manual_parameters=[
        openapi.Parameter('post_id', openapi.IN_PATH, description="게시글 ID", type=openapi.TYPE_INTEGER)
    ],
    responses={200: openapi.Response('성공', PostDetailSerializer, examples={"application/json": post_response_example}), 404: '게시글을 찾을 수 없습니다'}
)
@swagger_auto_schema(
    method='delete',
    operation_summary="신고된 게시글 삭제",
    operation_description="특정 ID의 신고된 게시글을 삭제합니다",
    manual_parameters=[
        openapi.Parameter('post_id', openapi.IN_PATH, description="게시글 ID", type=openapi.TYPE_INTEGER)
    ],
    responses={204: '게시글이 삭제되었습니다', 404: '게시글을 찾을 수 없습니다'}
)
@api_view(['GET', 'DELETE'])
@permission_classes([IsAdminUser])  # 관리자만 접근 가능
def reported_post_detail(request, post_id):
    try:
        post = Post.objects.get(id=post_id, reported_by__isnull=False)
    except Post.DoesNotExist:
        return Response({"error": "게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PostDetailSerializer(post)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        post.delete()
        return Response({"message": "게시글이 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='get',
    operation_summary="신고된 댓글 조회",
    operation_description="신고된 모든 댓글을 조회합니다",
    responses={200: openapi.Response('성공', CommentSerializer(many=True), examples={"application/json": [comment_response_example]})}
)
@api_view(['GET'])
@permission_classes([IsAdminUser])  # 관리자만 접근 가능
def reported_comments_list(request):
    comments = Comment.objects.filter(reported_by__isnull=False).distinct()
    paginator = TenResultsSetPagination()
    result_page = paginator.paginate_queryset(comments, request)
    serializer = CommentSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@swagger_auto_schema(
    method='get',
    operation_summary="신고된 댓글 상세 조회",
    operation_description="특정 ID의 신고된 댓글을 조회합니다",
    manual_parameters=[
        openapi.Parameter('comment_id', openapi.IN_PATH, description="댓글 ID", type=openapi.TYPE_INTEGER)
    ],
    responses={200: openapi.Response('성공', CommentSerializer, examples={"application/json": comment_response_example}), 404: '댓글을 찾을 수 없습니다'}
)
@swagger_auto_schema(
    method='delete',
    operation_summary="신고된 댓글 삭제",
    operation_description="특정 ID의 신고된 댓글을 삭제합니다",
    manual_parameters=[
        openapi.Parameter('comment_id', openapi.IN_PATH, description="댓글 ID", type=openapi.TYPE_INTEGER)
    ],
    responses={204: '댓글이 삭제되었습니다', 404: '댓글을 찾을 수 없습니다'}
)
@api_view(['GET', 'DELETE'])
@permission_classes([IsAdminUser])  # 관리자만 접근 가능
def reported_comment_detail(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, reported_by__isnull=False)
    except Comment.DoesNotExist:
        return Response({"error": "댓글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        comment.delete()
        return Response({"message": "댓글이 성공적으로 삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
from rest_framework.exceptions import ValidationError

@swagger_auto_schema(
    method='post',
    operation_summary="게시글 좋아요/좋아요 취소",
    manual_parameters=[
        openapi.Parameter('board_type', openapi.IN_PATH, description="게시판 타입", type=openapi.TYPE_STRING),
        openapi.Parameter('pk', openapi.IN_PATH, description="게시글 ID", type=openapi.TYPE_INTEGER)
    ],
    operation_description="게시글에 좋아요를 누르거나 좋아요를 취소합니다",
    responses={
        200: openapi.Response(description="요청이 성공적으로 처리되었습니다.", examples={"application/json": {"message": "좋아요가 완료되었습니다"}}),
        404: openapi.Response(description="게시글을 찾을 수 없습니다.", examples={"application/json": {"error": "게시글을 찾을 수 없습니다"}})
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def like_post(request, board_type, pk):
    try:
        post = Post.objects.get(pk=pk, board_type=board_type)
    except Post.DoesNotExist:
        return Response({"error": "게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    if request.user in post.liked_users.all():
        post.liked_users.remove(request.user)
        return Response({"message": "좋아요가 취소되었습니다."}, status=status.HTTP_200_OK)
    else:
        post.liked_users.add(request.user)
        return Response({"message": "좋아요가 완료되었습니다."}, status=status.HTTP_200_OK)