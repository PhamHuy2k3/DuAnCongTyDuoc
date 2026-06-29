from django.db import models
from django.conf import settings
from django.utils import timezone


class MedicineItem(models.Model):
    trade_name = models.CharField(max_length=255, verbose_name="Tên thương mại")
    active_ingredient = models.CharField(max_length=255, verbose_name="Hoạt chất")
    strength = models.CharField(max_length=100, verbose_name="Hàm lượng")
    dosage_form = models.CharField(max_length=100, verbose_name="Dạng bào chế")
    manufacturer = models.CharField(max_length=255, blank=True, verbose_name="Nhà sản xuất")
    batch_number = models.CharField(max_length=100, verbose_name="Số lô")
    registration_number = models.CharField(max_length=100, blank=True, verbose_name="Số đăng ký")
    mfg_date = models.CharField(max_length=50, blank=True, verbose_name="Ngày sản xuất")
    exp_date = models.CharField(max_length=50, verbose_name="Hạn sử dụng")
    indications = models.TextField(blank=True, verbose_name="Chỉ định")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Người duyệt"
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày duyệt")

    class Meta:
        verbose_name = "Dược phẩm"
        verbose_name_plural = "Dược phẩm"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.trade_name} - {self.batch_number}"


class ScannedDocument(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name="Người quét"
    )
    file_name = models.CharField(max_length=255, verbose_name="Tên tệp")
    scanned_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày quét")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='pending', verbose_name="Trạng thái"
    )
    accuracy_score = models.FloatField(default=0.0, verbose_name="Độ chính xác")
    medicine = models.OneToOneField(
        MedicineItem, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Dược phẩm"
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_docs',
        verbose_name="Người kiểm duyệt"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Ngày duyệt")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")

    class Meta:
        verbose_name = "Tài liệu đã quét"
        verbose_name_plural = "Tài liệu đã quét"
        ordering = ['-scanned_at']

    def __str__(self):
        return f"{self.file_name} ({self.get_status_display()})"
