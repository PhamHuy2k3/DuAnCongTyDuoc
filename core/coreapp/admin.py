from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Cập nhật danh sách hiển thị
    list_display = ('email', 'username', 'role', 'is_password_changed', 'is_staff', 'is_active')
    
    search_fields = ('email', 'username')
    
    # Lọc theo vai trò mới
    list_filter = ('role', 'is_password_changed', 'is_staff', 'is_active')
    
    ordering = ('-date_joined',)

    # Cấu hình fieldsets để hiển thị các trường tùy chỉnh trong Admin panel
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin PharmaScan', {'fields': ('role', 'phone_number', 'is_password_changed', 'plain_password_temp', 'birth_date')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin PharmaScan', {'fields': ('role', 'phone_number', 'birth_date')}),
    )