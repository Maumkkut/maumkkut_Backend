from django.shortcuts import redirect
from decouple import config
from django.http import JsonResponse
from django.contrib.auth import login, get_user_model
import requests
from rest_framework import status
from allauth.socialaccount.models import SocialAccount

CLIENT_ID = config('GOOGLE_CLIENT_ID')
CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = config('GOOGLE_REDIRECT')
TOKEN_URI = config('GOOGLE_TOKEN_URI')

def google_login(request):
    auth_url = (
        f'https://accounts.google.com/o/oauth2/v2/auth?'
        f'client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&'
        f'response_type=code&scope=email profile&access_type=offline'
    )
    return redirect(auth_url)

def google_callback(request):
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
            # 새로 생성된 사용자에 대한 추가 설정을 여기에 추가할 수 있습니다.
            pass
        
        # 사용자를 Django 세션에 로그인
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # 성공적으로 로그인 했음을 클라이언트에게 알림
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
