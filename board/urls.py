from . import views
from django.urls import path

urlpatterns = [
    # 자유게시판 URL 패턴
    path('free-board/', views.free_post_list, name='free-post-list'),
    path('free-board/<int:pk>/', views.free_post_detail, name='free_post_detail'),
    path('free-board/<int:post_id>/comments/', views.free_comment_list, name='free_comment_list'),
    path('free-board/<int:post_id>/comments/<int:comment_id>/', views.free_comment_operations, name='free_comment_operations'),
    path('free-board/<int:post_id>/comments/<int:comment_id>/detail/', views.free_comment_detail, name='free_comment_detail'),

    # 여행 후기 게시판 URL 패턴
    path('travel-board/', views.travel_post_list, name='travel-post-list'),
    path('travel-board/<int:pk>/', views.travel_post_detail, name='travel_post_detail'),
    path('travel-board/<int:post_id>/comments/', views.travel_comment_list, name='travel_comment_list'),
    path('travel-board/<int:post_id>/comments/<int:comment_id>/', views.travel_comment_operations, name='travel_comment_operations'),
    path('travel-board/<int:post_id>/comments/<int:comment_id>/detail/', views.travel_comment_detail, name='travel_comment_detail'),

    # 통합 신고 기능 URL 패턴
    # item_type -> post 게시글, comment 댓글
    path('report/<str:item_type>/<int:item_id>/', views.report_item, name='report-item'),

    # 공통 조회 기능 URL 패턴
    path('posts/search/day/', views.search_posts_day, name='search_posts_day'),
    path('posts/search/week/', views.search_posts_week, name='search_posts_week'),
    path('posts/search/month/', views.search_posts_month, name='search_posts_month'),
    path('posts/search/year/', views.search_posts_year, name='search_posts_year'),
]
