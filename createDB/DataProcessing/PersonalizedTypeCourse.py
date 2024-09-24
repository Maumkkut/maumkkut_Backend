from datetime import datetime
from django.shortcuts import render
from django.conf import settings
from ..models import GroupInfo, Group_Members, Tours, Routes_plan, Tour_plan_data
from django.shortcuts import get_object_or_404, get_list_or_404
from geopy.distance import geodesic

###########################################################################################################
# 개인
########################################################################################################### 

region_codes = {
    "강릉": 1,
    "고성": 2,
    "동해": 3,
    "삼척": 4,
    "속초": 5,
    "양구": 6,
    "양양": 7,
    "영월": 8,
    "원주": 9,
    "인제": 10,
    "정선": 11,
    "철원": 12,
    "춘천": 13,
    "태백": 14,
    "평창": 15,
    "홍천": 16,
    "화천": 17,
    "횡성": 18
}

def expand_cat3_ranges(cat3_ranges):
    expanded_cat3 = []
    for cat3_range in cat3_ranges:
        start, end = cat3_range.split(' ~ ')
        start_prefix = start[:-2]
        start_suffix = int(start[-2:])
        end_suffix = int(end[-2:])
        
        for i in range(start_suffix, end_suffix + 1):
            expanded_cat3.append(f"{start_prefix}{i:02d}")
    
    return expanded_cat3



def get_tour_courses(character_type):
    character_courses = {
        "힐링형 감자": {
            'type_ids': [12, 14, 32],
            'cat3_ranges': ['A01010100 ~ A01020200', 'A02010800 ~ A02010800', 'A02020300 ~ A02020800', 'A03030500 ~ A03030600'],
            'cat2': ['A0101', 'A0201', 'A0202', 'A0303']
        },
        "액티비티형 옥수수": {
            'type_ids': [28, 12, 25],
            'cat3_ranges': ['A03010200 ~ A03050100', 'A02020400 ~ A02020500'],
            'cat2': ['A0301', 'A0305', 'A0202']
        },
        "관람형 곤드레": {
            'type_ids': [14, 12, 25],
            'cat3_ranges': ['A02010100 ~ A02011000', 'A02030200 ~ A02030300', 'A02050200 ~ A02050200', 'A02060100 ~ A02060500', 'A04010700 ~ A04010700'],
            'cat2': ['A0201', 'A0203', 'A0205', 'A0206', 'A0401']
        },
        "미식가형 송이": {
            'type_ids': [39, 38, 12],
            'cat3_ranges': ['A05020700 ~ A05020900', 'A04010100 ~ A04010200', 'A02030100 ~ A02030100', 'A02040600 ~ A02040600'],
            'cat2': ['A0502', 'A0401', 'A0203', 'A0204']
        },
        "사람좋아 쌀알": {
            'type_ids': [15, 12, 14],
            'cat3_ranges': ['A01011200 ~ A01011200', 'A02020400 ~ A02020800', 'A02030600 ~ A02030600', 'A02060400 ~ A02060400', 'A03021200 ~ A03021400', 'A03030800 ~ A03030800'],
            'cat2': ['A0101', 'A0202', 'A0203', 'A0206', 'A0302', 'A0303']
        },
        "도전형 인삼": {
            'type_ids': [25, 28, 12],
            'cat3_ranges': ['A02030100 ~ A02030400', 'A02020200 ~ A02020600', 'A03021800 ~ A03022400', 'A03030200 ~ A03030400', 'A03040300 ~ A03040400'],
            'cat2': ['A0203', 'A0202', 'A0302', 'A0303', 'A0305']
        },
        "인플루언서형 복숭아": {
            'type_ids': [15, 14, 12],
            'cat3_ranges': ['A01011200 ~ A01011200', 'A02020800 ~ A02020800', 'A02030600 ~ A02030600', 'A02050200 ~ A02050600', 'A02060100 ~ A02060500'],
            'cat2': ['A0101', 'A0202', 'A0203', 'A0205', 'A0206']
        },
        "나무늘보형 순두부": {
            'type_ids': [32, 12, 39],
            'cat3_ranges': ['A02010800 ~ A02010800', 'A02020300 ~ A02020600', 'A05020900 ~ A05020900'],
            'cat2': ['A0201', 'A0202', 'A0203', 'A0502']
        }
    }
    
    course_info = character_courses.get(character_type, None)
    if course_info:
        course_info['cat3'] = expand_cat3_ranges(course_info['cat3_ranges'])
    return course_info

# 소분류 우선 만약 소분류로 했을때 결과가 없으면 중분류까지 감
def filter_courses_by_preference(tour_courses, cat3_list, cat2_list):
    # 소분류 코드(cat3)로 필터링
    filtered_courses = [course for course in tour_courses if course.cat3 in cat3_list]
    # 소분류 코드로 필터링된 결과가 없으면 중분류 코드(cat2)로 필터링
    if not filtered_courses:
        filtered_courses = [course for course in tour_courses if course.cat2 in cat2_list]
    return filtered_courses


# 거리 계산 - 코스 추천시 코스별 거리가 멀면 안되기에
def filter_courses_by_distance(courses, base_location, max_distance=1.0):
    filtered_courses = []
    for course in courses:
        distance = geodesic((base_location.mapy, base_location.mapx), (course.mapy, course.mapx)).km
        if distance <= max_distance:
            filtered_courses.append(course)
    return filtered_courses


# 행사나 이벤트와 같이 종료 조건이 있다면 해당 날에 가능한지 여부파악
def filter_ongoing_events(courses):
    ongoing_courses = []
    today = datetime.today().date()
    for course in courses:
        if not course.eventenddate or course.eventenddate.date() >= today:
            ongoing_courses.append(course)
    return ongoing_courses


# 계절에 맞는 추천인지 확인
def filter_seasonal_courses(courses):
    seasonal_courses = []
    current_month = datetime.now().month
    for course in courses:
        # 눈썰매장, 스키/스노보드
        if course.cat3 in ["A03021200", "A03021400"] and (current_month in [12, 1, 2, 3]):
            seasonal_courses.append(course)
        # 수상 스포츠
        elif course.cat2 == "A0303" and (current_month in [6, 7, 8, 9]):
            seasonal_courses.append(course)
        else:
            seasonal_courses.append(course)
    return seasonal_courses


# 아침, 점심, 저녁대 별로 다르게 검색
def filter_courses_by_time(courses, time_of_day):
    time_filtered_courses = []
    for course in courses:
        if time_of_day == "morning" and course.type_id in [12, 14, 15, 28]:  # 아침: 관광지, 문화시설, 행사/공연/축제, 레포츠,
            time_filtered_courses.append(course)
        elif time_of_day == "afternoon" and course.type_id in [12, 14, 15, 28]:  # 점심: 관광지, 문화시설, 행사/공연/축제, 레포츠,
            time_filtered_courses.append(course)
        elif time_of_day == "evening" and course.type_id in [12, 38]:  # 저녁: 관광지,쇼핑
            time_filtered_courses.append(course)
    return time_filtered_courses


# 여유로움의 중요도에 따른 코스 개수 변경
def build_course_pattern(courses, food_courses, relaxation, food_importance, max_distance=1.0):
    pattern = []
    used_courses = set()
    
    if relaxation <= 2:
        course_count = 6
    elif relaxation == 3:
        course_count = 5
    else:
        course_count = 4

    selected_courses = courses[:course_count]
    
    current_location = selected_courses[0] if selected_courses else None

    for i in range(len(selected_courses) - 1):
        pattern.append(selected_courses[i])
        filtered_food_courses = filter_courses_by_distance(food_courses, selected_courses[i], max_distance)
        if filtered_food_courses:
            pattern.append(filtered_food_courses[0])  # 가장 가까운 음식점 추가
        current_location = selected_courses[i]

    pattern.append(selected_courses[-1])  # 마지막 놀거리 추가

    return pattern



# 개인 코스 추천
# input -> [1,1,1,1,1,1,1,1,1,2],'힐링형 감자','강릉'
def recommend_course_view(importance_list, travel_character, region):
    relaxation = importance_list[0]
    food_importance = importance_list[4]

    course_info = get_tour_courses(travel_character)
    type_ids = course_info['type_ids']
    cat3_list = course_info['cat3']
    cat2_list = course_info['cat2']
    
    sigungucode = region_codes.get(region)
    if not sigungucode:
        return {"error": "해당 지역에 대한 정보가 없습니다."}
    
    # 놀거리 데이터 가져오기
    tour_courses = list(Tours.objects.filter(type_id__in=type_ids, sigungucode=sigungucode))
    if not tour_courses:
        return {"error": "해당 지역에 대한 정보가 없습니다."}
    
    # 종료된 행사/이벤트 제외
    tour_courses = filter_ongoing_events(tour_courses)
    
    # 계절에 맞는 코스 필터링
    tour_courses = filter_seasonal_courses(tour_courses)
    
    # 캐릭터 취향에 맞는 코스 필터링
    tour_courses = filter_courses_by_preference(tour_courses, cat3_list, cat2_list)
    
    # 시간대에 맞는 코스 필터링
    morning_courses = filter_courses_by_time(tour_courses, "morning")
    afternoon_courses = filter_courses_by_time(tour_courses, "afternoon")
    evening_courses = filter_courses_by_time(tour_courses, "evening")
    tour_courses = morning_courses + afternoon_courses + evening_courses
    
    # 음식점 데이터 가져오기
    food_courses = list(Tours.objects.filter(type_id=39, sigungucode=sigungucode))
    if not food_courses:
        return {"error": "해당 지역에 음식점 정보가 없습니다."}

    result = build_course_pattern(tour_courses, food_courses, relaxation, food_importance)
    
    result_list = [{"title": course.title, "addr1": course.addr1, "mapx": course.mapx, "mapy": course.mapy} for course in result]

    return result_list


