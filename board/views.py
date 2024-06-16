from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db.models import Q
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list(request):
    #단순 전체 조회
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
    #프론트에서 keyword랑 method로 보내줘야함
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
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_list(request, post_id):
    if request.method == 'GET':
        comments = Comment.objects.filter(post_id=post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post_id=post_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)