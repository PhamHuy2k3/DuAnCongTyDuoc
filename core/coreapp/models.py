from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('USER', 'Người dùng'),
        ('ADMIN', 'Quản trị viên'),
    ]

    email = models.EmailField(unique=True, verbose_name="Địa chỉ Email")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    
    is_password_changed = models.BooleanField(default=False, verbose_name="Đã đổi mật khẩu")
    password_reset_required = models.BooleanField(default=False, verbose_name="Yêu cầu đặt lại mật khẩu")
    
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

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
