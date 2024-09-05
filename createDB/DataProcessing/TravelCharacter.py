from .CharacterRecommendations import characters
# input -> importance_list > [4,2,1,4,5,6,7,8,2,0]
def recommend_character(importance_list):
    # 캐릭터 목록을 정의 (각 캐릭터의 이름, 키워드 중요도, 설명)


    # 키워드 목록
    keywords = [
        "힐링", "여유로움", "자연", "관람", "음식점", "모험","액티비티","많은", "쇼핑", "사진 촬영"
    ]

    # 입력된 중요도를 choices 딕셔너리에 매핑
    choices = {keywords[i]: importance_list[i] for i in range(len(keywords))}

    best_match = None
    best_score = float('-inf')

    # 각 캐릭터의 점수를 계산
    for character in characters:
        # 캐릭터의 각 키워드 가중치와 사용자의 중요도를 곱한 값을 합산하여 점수 계산
        score = sum(choices.get(key, 0) * character["keywords"].get(key, 0) for key in choices)
        # 가장 높은 점수를 받은 캐릭터를 best_match로 설정
        if score > best_score:
            best_match = character
            best_score = score

    return best_match['name'], best_match['description'], best_match['recommended_place'], best_match['reason'], best_match['best_match'], best_match['match_reason']