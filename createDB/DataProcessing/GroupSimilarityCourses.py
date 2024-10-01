from datetime import datetime
from ..models import GroupInfo, Group_Members, Routes_plan, User_info
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from accounts.models import Group

###########################################################################################################
# 단체                                                 
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

# 중요도를 기반으로 가중치 리스트 생성
def create_weighted_list(preferences):
    weighted_list = []
    keywords = [
        "힐링", "여유로움", "자연", "관람", "음식점", "모험", "액티비티", "사람 많은 곳", "쇼핑", "사진 촬영"
    ]
    for pref in preferences:
        for i, weight in enumerate(pref):
            weighted_list.extend([keywords[i]] * weight)
    return weighted_list

# 중요도를 리스트 형태로 가져오는 함수
def get_importance_list(user_info):
    importance_list = []
    importance_mapping = {
        '힐링': user_info.user_healing,
        '여유로움': user_info.user_relax,
        '자연': user_info.user_nature,
        '관람': user_info.user_exhibit,
        '음식점': user_info.user_food,
        '모험': user_info.user_adventure,
        '사람 많은 곳': user_info.user_people,
        '쇼핑': user_info.user_shopping,
        '사진 촬영': user_info.user_photo,
    }
    
    for key, value in importance_mapping.items():
        importance_list.extend([key] * value)
    
    return importance_list

# 코사인 유사도 계산
def calculate_cosine_similarity(group1, group2):
    vectorizer = CountVectorizer().fit_transform([' '.join(group1), ' '.join(group2)])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors)[0][1]

# 유사한 그룹 찾기
def find_similar_group(current_group_preferences, groups_data):
    max_similarity = float('-inf')
    most_similar_group = None

    for group_data in groups_data:
        group_preferences = group_data['preferences']
        similarity = calculate_cosine_similarity(current_group_preferences, group_preferences)
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_group = group_data

    return most_similar_group


# input -> group_id(int)
def recommend_similar_group(group, current_group_id, target_area):
    # 지역명을 숫자 코드로 변환
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
    
    # target_area를 숫자 코드로 변환
    area_code = region_codes.get(target_area)
    if area_code is None:
        return {"error": "유효하지 않은 지역입니다."}
    
    # 현재 그룹의 구성원들의 중요도 리스트를 가져옴
    group_members = group.get_members_with_leader()
    current_group_preferences = []
    for member in group_members:
        user_info = member.user_info_set.first()
        if not user_info:
            user_info, created = User_info.objects.get_or_create(user=member)
        if user_info:
            current_group_preferences.append(get_importance_list(user_info))
        
    if not current_group_preferences:
        return {"error": "현재 그룹에 구성원이 없습니다."}

    current_group_weighted_list = sum(current_group_preferences, [])

    # 특정 지역(area_code)에 해당하는 그룹만 필터링
    filtered_groupinfos = GroupInfo.objects.filter(routes_plan__route_area=area_code).exclude(id=current_group_id).distinct()

    groups_data = []
    for groupinfo in filtered_groupinfos:
        group = groupinfo.group
        group_members = group.get_members_with_leader()
        group_preferences = []
        for member in group_members:
            user_info = member.user_info_set.first()
            if user_info:
                group_preferences.append(get_importance_list(user_info))
        if group_preferences:
            group_weighted_list = sum(group_preferences, [])
            groups_data.append({'id': group.id, 'preferences': group_weighted_list})

    # 가장 유사한 그룹 찾기
    similar_group = find_similar_group(current_group_weighted_list, groups_data)

    if not similar_group:
        return {"error": "유사한 그룹을 찾을 수 없습니다."}

    similar_group_id = similar_group['id']
    similar_group_routes = Routes_plan.objects.filter(group_id=similar_group_id, route_area=area_code)

    if not similar_group_routes.exists():
        return {"error": "해당 그룹의 코스를 찾을 수 없습니다."}

    # 첫 번째 코스만 반환
    selected_route = similar_group_routes.first()
    print(selected_route.id)
    tour_info_list = [
        {
            "tour_id": tour.id,
            "title": tour.title,
            "addr1": tour.addr1,
            "mapx": tour.mapx,
            "mapy": tour.mapy
        }
        for tour in selected_route.route_details.all()
    ]
    for tour in selected_route.route_details.all():
        print(tour)

    result = {
        "route_id":selected_route.id,
        "route_name": selected_route.route_name,
        "lodge": selected_route.lodge,
        "route_area": selected_route.route_area,
        "tour_startdate": selected_route.tour_startdate,
        "tour_enddate": selected_route.tour_enddate,
        "group_id": selected_route.group_id,
        "tour_info_list": tour_info_list
    }

    return result