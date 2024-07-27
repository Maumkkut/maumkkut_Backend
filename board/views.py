from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer

# 자유게시판 뷰
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def free_post_list(request):
    if request.method == 'GET':
        posts = Post.objects.filter(board_type='free')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, board_type='free')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def free_post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk, board_type='free')
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = PostSerializer(post)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def free_comment_list(request, post_id):
    comments = Comment.objects.filter(post_id=post_id)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def free_comment_detail(request, post_id, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, post_id=post_id)
    except Comment.DoesNotExist:
        return Response({"error": "댓글이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        replies = comment.replies.all()
        serializer = CommentSerializer(replies, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post_id=post_id, parent_comment=comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def free_comment_operations(request, post_id, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, post_id=post_id)
    except Comment.DoesNotExist:
        return Response({"error": "댓글이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

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
        return Response(status=status.HTTP_204_NO_CONTENT)

# 여행 후기 게시판 뷰
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def travel_post_list(request):
    if request.method == 'GET':
        posts = Post.objects.filter(board_type='travel')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, board_type='travel')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def travel_post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk, board_type='travel')
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = PostSerializer(post)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def travel_comment_list(request, post_id):
    comments = Comment.objects.filter(post_id=post_id)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def travel_comment_detail(request, post_id, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, post_id=post_id)
    except Comment.DoesNotExist:
        return Response({"error": "댓글이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        replies = comment.replies.all()
        serializer = CommentSerializer(replies, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post_id=post_id, parent_comment=comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def travel_comment_operations(request, post_id, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, post_id=post_id)
    except Comment.DoesNotExist:
        return Response({"error": "댓글이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

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
        return Response(status=status.HTTP_204_NO_CONTENT)

# 통합 신고 기능
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def report_item(request, item_type, item_id):
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

    item.report_count += 1
    item.save()
    return Response({'message': '신고가 완료되었습니다.'}, status=status.HTTP_200_OK)

# 공통 조회 뷰
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def search_posts_day(request):
    date_from = timezone.now() - timedelta(days=1)
    posts = Post.objects.filter(created_at__gte=date_from)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def search_posts_week(request):
    date_from = timezone.now() - timedelta(weeks=1)
    posts = Post.objects.filter(created_at__gte=date_from)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def search_posts_month(request):
    date_from = timezone.now() - timedelta(days=30)
    posts = Post.objects.filter(created_at__gte=date_from)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def search_posts_year(request):
    date_from = timezone.now() - timedelta(days=365)
    posts = Post.objects.filter(created_at__gte=date_from)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)
