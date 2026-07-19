from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


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


class SystemLog(models.Model):
    """Nhật ký hoạt động hệ thống - chỉ Admin được xem."""

    ACTION_CHOICES = [
        ('LOGIN', 'Đăng nhập'),
        ('LOGIN_FAILED', 'Đăng nhập thất bại'),
        ('LOGOUT', 'Đăng xuất'),
        ('USER_CREATED', 'Tạo tài khoản'),
        ('USER_DELETED', 'Xóa tài khoản'),
        ('PASSWORD_RESET', 'Đặt lại mật khẩu'),
        ('PASSWORD_CHANGED', 'Đổi mật khẩu'),
        ('USER_LOCKED', 'Khóa tài khoản'),
        ('USER_UNLOCKED', 'Mở khóa tài khoản'),
        ('DOC_APPROVED', 'Duyệt tài liệu'),
        ('DOC_REJECTED', 'Từ chối tài liệu'),
        ('MEDICINE_DELETED', 'Xóa dược phẩm'),
    ]

    actor = models.ForeignKey(
        'CustomUser', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='system_logs',
        verbose_name="Người thực hiện",
    )
    action = models.CharField(
        max_length=30, choices=ACTION_CHOICES,
        verbose_name="Hành động",
    )
    target_type = models.CharField(
        max_length=50, blank=True, default='',
        verbose_name="Loại đối tượng",
    )
    target_id = models.IntegerField(
        null=True, blank=True,
        verbose_name="ID đối tượng",
    )
    target_label = models.CharField(
        max_length=255, blank=True, default='',
        verbose_name="Tên đối tượng",
    )
    detail = models.JSONField(
        default=dict, blank=True,
        verbose_name="Chi tiết thay đổi",
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        verbose_name="Địa chỉ IP",
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name="Thời điểm",
    )

    class Meta:
        verbose_name = "Nhật ký hệ thống"
        verbose_name_plural = "Nhật ký hệ thống"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['actor']),
        ]

    def __str__(self):
        actor_name = self.actor.username if self.actor else 'Hệ thống'
        return f"[{self.get_action_display()}] {actor_name} → {self.target_label}"

