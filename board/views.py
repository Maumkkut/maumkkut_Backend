from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db.models import Q
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from django.utils import timezone
from datetime import timedelta

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list_day(request):
    date_from = timezone.now() - timedelta(days=1)
    posts = Post.objects.filter(created_at__gte=date_from)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list_week(request):
    date_from = timezone.now() - timedelta(weeks=1)
    posts = Post.objects.filter(created_at__gte=date_from)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list_month(request):
    date_from = timezone.now() - timedelta(days=30)
    posts = Post.objects.filter(created_at__gte=date_from)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list_year(request):
    date_from = timezone.now() - timedelta(days=365)
    posts = Post.objects.filter(created_at__gte=date_from)
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_detail(request, pk):
    try:
        post = Post.objects.get(pk=pk)
    except Post.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if post.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if post.author != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
#키워드 기반 검색
def search_posts(request, method):
    #프론트에서 keyword 및 method를 보내줘야함
    keyword = request.GET.get('keyword', None)
    method = request.GET.get('method', 'title_content')
    
    if keyword:
        if method == 'title_content':
            posts = Post.objects.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))
        elif method == 'title':
            posts = Post.objects.filter(title__icontains=keyword)
        elif method == 'comment':
            posts = Post.objects.filter(comments__content__icontains=keyword).distinct()
        elif method == 'author':
            posts = Post.objects.filter(author__username__icontains=keyword)
        else:
            posts = Post.objects.none()
        
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    return Response({"error": "Keyword not provided."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
# @authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_detail(request, post_id, comment_id):
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
def comment_operations(request, post_id, comment_id):
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

    
# 코멘트 상세 조회   
# def comment_detail(request, post_id, comment_id):
#     try:
#         comment = Comment.objects.get(id=comment_id, post_id=post_id)
#     except Comment.DoesNotExist:
#         return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'GET':
#         replies = comment.replies.all()
#         serializer = CommentSerializer(replies, many=True)
#         return Response(serializer.data)

#     elif request.method == 'POST':
#         serializer = CommentSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(author=request.user, post_id=post_id, parent_comment=comment)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
