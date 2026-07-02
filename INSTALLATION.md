# HƯỚNG DẪN CẢI THIỆN VÀ MIGRATION

## 1. Cài đặt dependencies mới

```bash
cd core
pip install -r ../requirements.txt
```

## 2. Tạo file .env

Tạo file `.env` trong thư mục `core/` (copy từ `.env.example`):

```bash
copy .env.example .env
```

Sau đó chỉnh sửa file `.env` với thông tin của bạn:
- SECRET_KEY: Tạo key mới tại https://djecrety.ir/
- EMAIL_HOST_USER: Email của bạn để gửi password reset
- EMAIL_HOST_PASSWORD: App password của Gmail

## 3. Tạo migrations cho model mới

```bash
python manage.py makemigrations
```

## 4. Chạy migrations

```bash
python manage.py migrate
```

Lưu ý: Nếu gặp lỗi với field `plain_password_temp`, chạy lệnh sau trước:

```bash
python manage.py shell
```

Trong shell:
```python
from coreapp.models import CustomUser
# Xóa dữ liệu plain_password_temp nếu cần
for user in CustomUser.objects.all():
    user.plain_password_temp = None
    user.save()
exit()
```

## 5. Tạo Groups cho roles

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import Group

Group.objects.get_or_create(name='USER')
Group.objects.get_or_create(name='ADMIN')
exit()
```

## 6. Chạy tests

```bash
python manage.py test coreapp
python manage.py test user
```

## 7. Chạy server

```bash
python manage.py runserver
```

## CÁC CẢI TIẾN ĐÃ THỰC HIỆN

### Bảo mật:
✅ Di chuyển SECRET_KEY ra .env file
✅ Xóa field plain_password_temp (không lưu password dạng plain text)
✅ Gửi password qua email thay vì hiển thị
✅ Thêm security headers cho production
✅ Validate file upload (size, extension)
✅ Xóa CSRF_EXEMPT khỏi upload endpoint
✅ Thêm validation cho input

### Code Quality:
✅ Tách business logic ra services.py
✅ Thêm validators.py cho input validation
✅ Thêm error handling và try-catch
✅ Thêm logging system
✅ Refactor views ngắn gọn hơn
✅ Thêm type hints và docstrings

### Performance:
✅ Thêm select_related() cho queries
✅ Thêm database indexes
✅ Giới hạn số lượng records (pagination)
✅ Giới hạn kích thước file upload

### Testing:
✅ Tạo test cases cơ bản
✅ Test models, services, validators
✅ Test authentication flow

### Configuration:
✅ Tạo .gitignore
✅ Tạo requirements.txt
✅ Thêm email configuration
✅ Thêm file upload limits
✅ Cấu hình logging với rotation

## NHỮNG GÌ CẦN LÀM TIẾP

1. **Cấu hình Email thực tế**:
   - Đăng ký Gmail App Password
   - Hoặc dùng SendGrid, AWS SES

2. **Thêm rate limiting**:
   - Cài django-ratelimit
   - Giới hạn login attempts

3. **Cải thiện frontend**:
   - Thêm loading states
   - Thêm client-side validation
   - Thêm progress bar cho upload

4. **Deploy checklist**:
   - Set DEBUG=False
   - Cấu hình HTTPS
   - Dùng PostgreSQL thay SQLite
   - Setup Redis cho cache
   - Cấu hình static files serving
   - Setup monitoring (Sentry)

5. **Thêm features**:
   - Password reset qua email
   - Two-factor authentication
   - Export data to Excel/PDF
   - Advanced search và filter
   - API endpoints với DRF
