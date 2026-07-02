import string
import secrets
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()
logger = logging.getLogger('coreapp')


def generate_secure_password(length=12):
    """Tạo mật khẩu ngẫu nhiên an toàn"""
    alphabet = string.ascii_letters + string.digits + "@#$%"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_password_email(user_email, username, password):
    """Gửi mật khẩu qua email"""
    try:
        subject = 'Thông tin tài khoản mới'
        message = f"""
Chào bạn,

Tài khoản của bạn đã được tạo thành công:
- Tên đăng nhập: {username}
- Email: {user_email}
- Mật khẩu tạm: {password}

Vui lòng đăng nhập và đổi mật khẩu ngay sau khi nhận được email này.

Trân trọng,
Hệ thống quản lý dược phẩm
"""
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        logger.info(f"Password email sent to {user_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {str(e)}")
        return False


class UserService:
    """Service xử lý logic liên quan đến User"""
    
    @staticmethod
    def create_user(username, email, fullname, role, birth_date=None, phone_number=None):
        """Tạo user mới"""
        try:
            # Validate
            if User.objects.filter(username=username).exists():
                return {'success': False, 'error': f"Tên đăng nhập '{username}' đã tồn tại!"}
            
            if User.objects.filter(email=email).exists():
                return {'success': False, 'error': f"Email '{email}' đã tồn tại!"}
            
            # Tạo password
            password = generate_secure_password()
            
            # Parse fullname
            name_parts = fullname.split(' ', 1)
            first_name = name_parts[1] if len(name_parts) > 1 else name_parts[0]
            last_name = name_parts[0] if len(name_parts) > 1 else ""
            
            # Tạo user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                birth_date=birth_date,
                phone_number=phone_number,
                is_password_changed=False,
                password_reset_required=True
            )
            
            # Thêm vào group
            group_map = {'USER': 'USER', 'ADMIN': 'ADMIN'}
            target_group_name = group_map.get(role)
            
            if target_group_name:
                try:
                    group = Group.objects.get(name=target_group_name)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    logger.warning(f"Group '{target_group_name}' không tồn tại")
            
            # Gửi email
            email_sent = send_password_email(email, username, password)
            
            logger.info(f"User {username} created successfully")
            
            return {
                'success': True,
                'user': user,
                'password': password,
                'email_sent': email_sent
            }
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def reset_password(username, new_password=None):
        """Reset mật khẩu user"""
        try:
            user = User.objects.get(username=username)
            
            if not new_password:
                new_password = generate_secure_password()
            
            user.set_password(new_password)
            user.is_password_changed = False
            user.password_reset_required = True
            user.save()
            
            # Gửi email
            email_sent = send_password_email(user.email, username, new_password)
            
            logger.info(f"Password reset for user {username}")
            
            return {
                'success': True,
                'password': new_password,
                'email_sent': email_sent
            }
            
        except User.DoesNotExist:
            logger.error(f"User {username} not found")
            return {'success': False, 'error': 'Không tìm thấy user'}
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def toggle_user_status(username, current_status):
        """Khóa/mở khóa user"""
        try:
            user = User.objects.get(username=username)
            user.is_active = (current_status != "lock")
            user.save()
            
            logger.info(f"User {username} status toggled to {user.is_active}")
            
            return {'success': True, 'user': user}
            
        except User.DoesNotExist:
            return {'success': False, 'error': 'Không tìm thấy user'}
        except Exception as e:
            logger.error(f"Error toggling user status: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def delete_user(username, current_user):
        """Xóa user"""
        try:
            user = User.objects.get(username=username)
            
            if user == current_user:
                return {'success': False, 'error': 'Bạn không thể tự xóa tài khoản của chính mình!'}
            
            user.delete()
            logger.info(f"User {username} deleted")
            
            return {'success': True}
            
        except User.DoesNotExist:
            return {'success': False, 'error': 'Tài khoản không tồn tại'}
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return {'success': False, 'error': str(e)}
