from datetime import datetime
from ..models import GroupInfo, Group_Members, Routes_plan, User_info
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from accounts.models import Group

###########################################################################################################
# 단체                                                 
###########################################################################################################

region_codes = {
    "강릉": 1, "고성": 2, "동해": 3, "삼척": 4, "속초": 5, "양구": 6, "양양": 7, "영월": 8,
    "원주": 9, "인제": 10, "정선": 11, "철원": 12, "춘천": 13, "태백": 14, "평창": 15,
    "홍천": 16, "화천": 17, "횡성": 18
}

def get_importance_list(user_info):
    importance_mapping = {
        '힐링': user_info.user_healing, '여유로움': user_info.user_relax,
        '자연': user_info.user_nature, '관람': user_info.user_exhibit,
        '음식점': user_info.user_food, '모험': user_info.user_adventure,
        '액티비티': user_info.user_activity,
        '사람 많은 곳': user_info.user_people, '쇼핑': user_info.user_shopping,
        '사진 촬영': user_info.user_photo,
    }
    return [key for key, value in importance_mapping.items() for _ in range(value)]

def calculate_cosine_similarity(group1, group2):
    vectorizer = CountVectorizer().fit_transform([' '.join(group1), ' '.join(group2)])
    vectors = vectorizer.toarray()
    return cosine_similarity(vectors)[0][1]

def find_similar_group(current_group_preferences, groups_data):
    max_similarity = float('-inf')
    most_similar_group = None
    for group_data in groups_data:
        similarity = calculate_cosine_similarity(current_group_preferences, group_data['preferences'])
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_group = group_data
    return most_similar_group

def recommend_similar_group(group, current_group_id, target_area):
    area_code = region_codes.get(target_area)
    if area_code is None:
        return {"error": "유효하지 않은 지역입니다."}
    
    group_members = group.get_members_with_leader()
    current_group_preferences = []
    for member in group_members:
        user_info = member.user_info_set.first()
        if not user_info:
            user_info, created = User_info.objects.get_or_create(user=member)
        if user_info:
            current_group_preferences.extend(get_importance_list(user_info))
    
    if not current_group_preferences:
        return {"error": "현재 그룹에 구성원이 없습니다."}

    filtered_groupinfos = GroupInfo.objects.filter(routes_plan__route_area=area_code).exclude(id=current_group_id).distinct()

    groups_data = []
    for groupinfo in filtered_groupinfos:
        group = groupinfo.group
        group_members = group.get_members_with_leader()
        group_preferences = []
        for member in group_members:
            user_info = member.user_info_set.first()
            if user_info:
                group_preferences.extend(get_importance_list(user_info))
        if group_preferences:
            groups_data.append({'id': group.id, 'preferences': group_preferences})

    similar_group = find_similar_group(current_group_preferences, groups_data)

    if not similar_group:
        return {"error": "유사한 그룹을 찾을 수 없습니다."}

    similar_group_id = similar_group['id']
    similar_group_routes = Routes_plan.objects.filter(group_id=similar_group_id, route_area=area_code)

    if not similar_group_routes.exists():
        return {"error": "해당 그룹의 코스를 찾을 수 없습니다."}

    result = []
    for selected_route in similar_group_routes.all():
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

        result.append({
            "route_id": selected_route.id,
            "route_name": selected_route.route_name,
            "lodge": selected_route.lodge,
            "route_area": selected_route.route_area,
            "tour_startdate": selected_route.tour_startdate,
            "tour_enddate": selected_route.tour_enddate,
            "group_id": selected_route.group_id,
            "tour_info_list": tour_info_list
        })

    # 모든 경로의 tour_info_list를 하나의 리스트로 합쳐서..
    all_tour_info = [tour for route in result for tour in route.get('tour_info_list', [])]

    return {
        "routes": result,
        "all_tour_info": all_tour_info
    }