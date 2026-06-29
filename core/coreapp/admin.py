from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'role', 'is_password_changed', 'is_staff', 'is_active')
    
    search_fields = ('email', 'username')
    
    list_filter = ('role', 'is_password_changed', 'is_staff', 'is_active')
    
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin PharmaScan', {'fields': ('role', 'phone_number', 'is_password_changed', 'plain_password_temp', 'birth_date')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin PharmaScan', {'fields': ('role', 'phone_number', 'birth_date')}),
    )
