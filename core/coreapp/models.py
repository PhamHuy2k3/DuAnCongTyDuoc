from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
class CustomUser(AbstractUser):
    # Chỉ định nghĩa 2 vai trò
    ROLE_CHOICES = [
        ('USER', 'Người dùng'),
        ('ADMIN', 'Quản trị viên'),
    ]

    email = models.EmailField(unique=True, verbose_name="Địa chỉ Email")
    # Đã xóa trường phone_number trùng lặp
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")
    
    plain_password_temp = models.CharField(max_length=128, blank=True, null=True, verbose_name="Mật khẩu tạm")
    birth_date = models.DateField(null=True, blank=True)
    
    # Mặc định is_password_changed nên là False nếu bạn muốn hệ thống bắt người dùng đổi pass lần đầu
    is_password_changed = models.BooleanField(default=False) 
    
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        default='USER', 
        verbose_name="Chức vụ / Vai trò"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 

    def __str__(self):
        return self.email
    
class UserActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=255)       
    path = models.CharField(max_length=500)         
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True) 

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{username} - {self.action} - {self.timestamp}"