from allauth.account.adapter import DefaultAccountAdapter

# 추가필드 저장
class CustomUserAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        from allauth.account.utils import user_field

        user = super().save_user(request, user, form, False)
        user_field(user, 'phone_number', request.data.get('phone_number'))
        user_field(user, 'address', request.data.get('address'))
        user_field(user, 'nickname', request.data.get('nickname'))
        user_field(user, 'date_of_birth', request.data.get('date_of_birth'))
        user.save()
        return user