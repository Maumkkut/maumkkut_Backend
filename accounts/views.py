from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth import login, get_user_model
import requests
from rest_framework import status
import os
from dj_rest_auth.registration.views import RegisterView
from .serializers import CustomRegisterSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.views import View

class TestView(View):
    def get(self, request):
        return JsonResponse({'status': 'Test view working!'}, status=status.HTTP_200_OK)
    
# class CustomRegisterView(RegisterView):
#     serializer_class = CustomRegisterSerializer
#     def get_response(self):
#         user = self.user
#         print(user)
#         # 커스텀 토큰 생성
#         tokens = self.get_tokens_for_user(user)
#         print(tokens)
#         return Response({
#             'refresh': tokens['refresh'],
#             'access': tokens['access'],
#         }, status=status.HTTP_201_CREATED)

#     def get_tokens_for_user(self, user):
#         refresh = RefreshToken.for_user(user)
#         return {
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#         }


    
def google_login(request):
    CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT')
    auth_url = (
        f'https://accounts.google.com/o/oauth2/v2/auth?'
        f'client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&'
        f'response_type=code&scope=email profile&access_type=offline'
    )
    return redirect(auth_url)

def google_callback(request):
    CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT')
    TOKEN_URI = os.environ.get('GOOGLE_TOKEN_URI')
    code = request.GET.get("code")
    
    if not code:
        return JsonResponse({"status": 400, "message": "Authorization code not provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    token_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
    
    token_req = requests.post(TOKEN_URI, data=token_data)

    if token_req.status_code != 200:
        return JsonResponse({"status": 400, "message": "Failed to fetch token from Google"}, status=status.HTTP_400_BAD_REQUEST)
    
    token_req_json = token_req.json()
    google_access_token = token_req_json.get('access_token')
    
    if not google_access_token:
        return JsonResponse({"status": 400, "message": "Access token not provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    email_response = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={google_access_token}")
    
    if email_response.status_code != 200:
        return JsonResponse({"status": 400, "message": "Failed to fetch email from Google"}, status=status.HTTP_400_BAD_REQUEST)
    
    email_res_json = email_response.json()
    email = email_res_json.get('email')
    
    if not email:
        return JsonResponse({"status": 400, "message": "Email not found in response"}, status=status.HTTP_400_BAD_REQUEST)
    
    User = get_user_model()

    try:
        user, created = User.objects.get_or_create(email=email, defaults={'username': email})
        
        # 소셜로그인 계정 유무 확인
        if created:
            # 새로 생성된 사용자에 대한 추가 설정
            pass
        
        # 사용자를 Django 세션에 로그인
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # 추가 정보 필요할 경우 리디렉션
        if not user.address or not user.nickname:
            return JsonResponse(
                {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                    },
                    "message": "Login successful, please complete your profile.",
                    "redirect_url": "http://localhost:5173/signin/loading"
                },
                status=status.HTTP_200_OK,
            )
        # 로그인 성공
        return JsonResponse(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "message": "Login successful",
            },
            status=status.HTTP_200_OK,
        )
    
    except User.DoesNotExist:
        return JsonResponse({"status": 404, "message": "User account does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return JsonResponse({"status": 400, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

def kakao_login(request):
    CLIENT_ID = os.environ.get("KAKAO_REST_API_KEY")
    REDIRECT_URI = os.environ.get("KAKAO_REDIRECT_URI")
    LOGIN_URI = os.environ.get("KAKAO_LOGIN_URI")
    
    uri = f"{LOGIN_URI}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"
    return redirect(uri)

def kakao_callback(request):
    CLIENT_ID = os.environ.get("KAKAO_REST_API_KEY")
    REDIRECT_URI = os.environ.get("KAKAO_REDIRECT_URI")
    CLIENT_SECRET = os.environ.get("KAKAO_CLIENT_SECRET_KEY")
    TOKEN_URI = os.environ.get("KAKAO_TOKEN_URI")
    code = request.GET.get("code")

    if not code:
        return JsonResponse({"status": 400, "message": "Authorization code not provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    token_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
    token_headers = {
        'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
    }
    token_req = requests.post(TOKEN_URI, data=token_data, headers=token_headers)

    if token_req.status_code != 200:
        return JsonResponse({"status": 400, "message": "Failed to fetch token from Kakao"}, status=status.HTTP_400_BAD_REQUEST)
    
    token_req_json = token_req.json()
    print(token_req_json)
    kakao_access_token = token_req_json.get('access_token')
    
    if not kakao_access_token:
        return JsonResponse({"status": 400, "message": "Access token not provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    user_info_url = os.environ.get("KAKAO_PROFILE_URI")
    user_info_headers = {
        'Authorization': f'Bearer {kakao_access_token}',
        'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
    }
    user_info_req = requests.get(user_info_url, headers=user_info_headers)
    
    if user_info_req.status_code != 200:
        return JsonResponse({"status": 400, "message": "Failed to fetch user info from Kakao"}, status=status.HTTP_400_BAD_REQUEST)
    
    user_info_json = user_info_req.json()
    print(user_info_json)
    kakao_account = user_info_json.get("kakao_account")

    if not kakao_account:
        return JsonResponse({"status": 400, "message": "Kakao account information not provided"}, status=status.HTTP_400_BAD_REQUEST)

    email = kakao_account.get("email")
    if not email:
        return JsonResponse({"status": 400, "message": "Email not provided by Kakao"}, status=status.HTTP_400_BAD_REQUEST)

    User = get_user_model()
    
    try:
        user, created = User.objects.get_or_create(email=email, defaults={'username': email})
        
        # 소셜로그인 계정 유무 확인
        if created:
            # 새로 생성된 사용자에 대한 추가 설정
            pass
        
        # 사용자를 Django 세션에 로그인
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # 추가 정보 필요할 경우 리디렉션
        if not user.address or not user.nickname:
            return JsonResponse(
                {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                    },
                    "message": "Login successful, please complete your profile.",
                    "redirect_url": "http://localhost:5173/signin/loading"
                },
                status=status.HTTP_200_OK,
            )
        # 로그인 성공
        return JsonResponse(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "message": "Login successful",
            },
            status=status.HTTP_200_OK,
        )
    
    except User.DoesNotExist:
        return JsonResponse({"status": 404, "message": "User account does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return JsonResponse({"status": 400, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
def check_user_info(request):
    user = request.user
    if user.is_authenticated:
        profile_complete = bool(user.phone_number)
        return JsonResponse({'profile_complete': profile_complete})
    return JsonResponse({"status": 401, "message": "인증되지 않은 사용자"})