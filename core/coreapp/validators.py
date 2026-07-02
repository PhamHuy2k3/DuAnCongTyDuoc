import re
from django.core.exceptions import ValidationError


def validate_phone_number(phone):
    """Validate số điện thoại Việt Nam"""
    if not phone:
        return True
    
    pattern = r'^(0|\+84)(3|5|7|8|9)[0-9]{8}$'
    if not re.match(pattern, phone):
        raise ValidationError('Số điện thoại không hợp lệ')
    return True


def validate_username(username):
    """Validate username"""
    if not username or len(username) < 3:
        raise ValidationError('Tên đăng nhập phải có ít nhất 3 ký tự')
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError('Tên đăng nhập chỉ được chứa chữ cái, số và dấu gạch dưới')
    
    return True


def validate_password(password):
    """Validate password strength"""
    if not password or len(password) < 8:
        raise ValidationError('Mật khẩu phải có ít nhất 8 ký tự')
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Mật khẩu phải có ít nhất 1 chữ hoa')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('Mật khẩu phải có ít nhất 1 chữ thường')
    
    if not re.search(r'[0-9]', password):
        raise ValidationError('Mật khẩu phải có ít nhất 1 chữ số')
    
    return True


def validate_file_extension(filename, allowed_extensions):
    """Validate file extension"""
    ext = filename.split('.')[-1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f'Chỉ chấp nhận file có đuôi: {", ".join(allowed_extensions)}')
    return True


def validate_file_size(file, max_size_mb=10):
    """Validate file size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidationError(f'Kích thước file không được vượt quá {max_size_mb}MB')
    return True
