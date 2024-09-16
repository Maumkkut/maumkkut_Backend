from . import views
from django.urls import path

urlpatterns = [
    # 지역별 랜덤 관광지 추천
    path('get_tours_by_area/<int:areacode>/', views.get_random_tours_by_area, name='get_random_tours_by_area'),

    # 지역별 및 유형별 랜덤 관광지 추천
    path('get_tours_by_tour_type/<int:areacode>/<str:tour_type>/', views.get_random_tours_by_tour_type, name='get_random_tours_by_tour_type'),

    # 관광 계획 데이터 조회(계획 PK 기준)
    path('get_routes_data_by_route/<int:route_pk>/', views.get_routes_data_by_route, name='get_routes_data_by_route'),

    # 지역별 관광 계획 데이터 조회
    path('get_routes_by_route_area/<int:areacode>/', views.get_routes_by_route_area, name='get_routes_by_route_area'),

    # 여행 유형별 관광 계획 데이터 조회
    path('get_routes_by_tour_type/<str:tour_type>/', views.get_routes_by_tour_type, name='get_routes_by_tour_type'),

    # 지역 및 여행 유형별 관광 계획 데이터 조회
    path('get_routes_by_tour_type_area/<int:areacode>/<str:tour_type>/', views.get_routes_by_tour_type_area, name='get_routes_by_tour_type_area'),

    # 여행 유형 캐릭터 추천
    # path('recommend_character/', views.recommend_character_view, name='recommend_character'),

    # 개인 여행지 추천
    path('recommend_course/', views.recommend_course_view, name='recommend_course'),

    # 단체 유사도 기반 여행지 추천
    path('recommend_similar_group/', views.recommend_similar_group_view, name='recommend_similar_group'),
]
