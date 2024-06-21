from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.core.validators import RegexValidator

phone_number_regex = RegexValidator(
        regex=r'^01(?:0|1|[6-9])-(\d{3,4})-(\d{4})$',
        message="입력 형식을 맞춰주세요.")

class CustomRegisterSerializer(RegisterSerializer):
    phone_number = serializers.CharField(
        required=True, 
        validators=[phone_number_regex], 
        help_text="휴대폰 번호 형식: 010-1234-5678")
    address = serializers.CharField(max_length=255, required=True)
    nickname = serializers.CharField(max_length=10, required=False)
    date_of_birth = serializers.DateField(required=False)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['phone_number'] = self.validated_data.get('phone_number', '')
        data['address'] = self.validated_data.get('address', '')
        data['nickname'] = self.validated_data.get('nickname', '')
        data['date_of_birth'] = self.validated_data.get('date_of_birth', '')
        return data
    
    def save(self, request):
        user = super().save(request)
        phone_number = self.validated_data.get('phone_number')
        address = self.validated_data.get('address')
        nickname = self.validated_data.get('nickname')
        date_of_birth = self.validated_data.get('date_of_birth')
        # db 저장 확인
        print(user)
        print("Saving user with phone number:", phone_number)
        print("Saving user with address:", address)
        print("Saving user with nickname:", nickname)
        print("Saving user with date_of_birth:", date_of_birth)
        user.phone_number = phone_number
        user.address = address
        user.date_of_birth = date_of_birth
        user.save()
        return user