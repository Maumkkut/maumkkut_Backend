from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'address', 'nickname', 'date_of_birth', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number', 'address', 'nickname', 'date_of_birth', 'role',)}),
    )
admin.site.register(User, CustomUserAdmin)
