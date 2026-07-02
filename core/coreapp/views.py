from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db.models import Q
import logging

from .services import UserService
from .validators import validate_username, validate_phone_number

logger = logging.getLogger('coreapp')


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render_by_role(request, request.user)


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')

        if not email or not password:
            return render(request, 'coreapp/login.html', {
                'error_message': "Vui lòng nhập đầy đủ email và mật khẩu!"
            })

        try:
            user = authenticate(request, username=email, password=password)
            
            if user is None:
                logger.warning(f"Failed login attempt for email: {email}")
                return render(request, 'coreapp/login.html', {
                    'error_message': "Sai email hoặc mật khẩu!"
                })
            
            if not user.is_active:
                logger.warning(f"Inactive user login attempt: {email}")
                return render(request, 'coreapp/login.html', {
                    'error_message': "Tài khoản của bạn đã bị khóa!"
                })
            
            login(request, user)
            
            if remember_me:
                request.session.set_expiry(1209600)  # 14 days
            else:
                request.session.set_expiry(0)
            
            logger.info(f"User {email} logged in successfully")
            return render_by_role(request, user)
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return render(request, 'coreapp/login.html', {
                'error_message': "Đã xảy ra lỗi. Vui lòng thử lại!"
            })

    return render(request, 'coreapp/login.html')


def logout_view(request):
    username = request.user.username if request.user.is_authenticated else 'Anonymous'
    logout(request)
    logger.info(f"User {username} logged out")
    return redirect('/login/')


def render_by_role(request, user):
    """Điều hướng theo role"""
    if user.role == 'ADMIN' or user.is_staff:
        return redirect('admin_dashboard')
        
    if user.role == 'USER':
        return render(request, 'user/home.html')
        
    logout(request)
    messages.error(request, "Tài khoản của bạn chưa được phân quyền truy cập.")
    logger.warning(f"User {user.email} has no valid role")
    return redirect('login')


def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or getattr(user, 'role', '') == 'ADMIN'


@login_required
@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    if request.method == "POST":
        action_type = request.POST.get("action_type")
        
        try:
            if action_type == "create_user":
                result = handle_create_user(request)
                if result['success']:
                    msg = f"Tạo tài khoản {result['username']} thành công."
                    if result.get('email_sent'):
                        msg += " Mật khẩu đã được gửi qua email."
                    else:
                        msg += f" Mật khẩu tạm: {result['password']}"
                    messages.success(request, msg)
                else:
                    messages.error(request, result['error'])
                    
            elif action_type == "reset_password":
                result = handle_reset_password(request)
                if result['success']:
                    msg = f"Đã reset mật khẩu cho {result['username']}"
                    if result.get('email_sent'):
                        msg += ". Mật khẩu mới đã được gửi qua email."
                    else:
                        msg += f". Mật khẩu mới: {result['password']}"
                    messages.success(request, msg)
                else:
                    messages.error(request, result['error'])
                    
            elif action_type == "toggle_status":
                result = handle_toggle_status(request)
                if result['success']:
                    messages.success(request, result['message'])
                else:
                    messages.error(request, result['error'])
                    
            elif action_type == "delete_user":
                result = handle_delete_user(request)
                if result['success']:
                    messages.success(request, result['message'])
                else:
                    messages.error(request, result['error'])
                    
        except Exception as e:
            logger.error(f"Admin dashboard error: {str(e)}")
            messages.error(request, "Đã xảy ra lỗi. Vui lòng thử lại!")
        
        return redirect('admin_dashboard')
    
    # GET request
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        all_users = User.objects.select_related().order_by('-date_joined')
        user_accounts = all_users.filter(role='USER')
        admin_accounts = all_users.filter(role='ADMIN')

        context = {
            'all_users': all_users,
            'user_accounts': user_accounts,
            'admin_accounts': admin_accounts,
        }
        return render(request, 'admin/admin.html', context)
        
    except Exception as e:
        logger.error(f"Error loading admin dashboard: {str(e)}")
        messages.error(request, "Không thể tải dữ liệu!")
        return render(request, 'admin/admin.html', {'all_users': [], 'user_accounts': [], 'admin_accounts': []})


def handle_create_user(request):
    """Xử lý tạo user mới"""
    try:
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        fullname = request.POST.get("fullname", "").strip()
        role = request.POST.get("role")
        birth_date = request.POST.get("birth_date") or None
        phone_number = request.POST.get("phone_number", "").strip() or None
        
        # Validate
        validate_username(username)
        if phone_number:
            validate_phone_number(phone_number)
        
        # Tạo user thông qua service
        result = UserService.create_user(
            username=username,
            email=email,
            fullname=fullname,
            role=role,
            birth_date=birth_date,
            phone_number=phone_number
        )
        
        if result['success']:
            result['username'] = username
        
        return result
        
    except ValidationError as e:
        return {'success': False, 'error': str(e)}
    except Exception as e:
        logger.error(f"Error in handle_create_user: {str(e)}")
        return {'success': False, 'error': 'Đã xảy ra lỗi khi tạo user'}


def handle_reset_password(request):
    """Xử lý reset password"""
    try:
        target_username = request.POST.get("target_username")
        new_password = request.POST.get("new_password", "").strip() or None
        
        result = UserService.reset_password(target_username, new_password)
        
        if result['success']:
            result['username'] = target_username
        
        return result
        
    except Exception as e:
        logger.error(f"Error in handle_reset_password: {str(e)}")
        return {'success': False, 'error': 'Đã xảy ra lỗi khi reset password'}


def handle_toggle_status(request):
    """Xử lý khóa/mở khóa user"""
    try:
        target_username = request.POST.get("target_username")
        current_status = request.POST.get("current_status")
        
        result = UserService.toggle_user_status(target_username, current_status)
        
        if result['success']:
            result['message'] = f"Đã cập nhật trạng thái cho {target_username}"
        
        return result
        
    except Exception as e:
        logger.error(f"Error in handle_toggle_status: {str(e)}")
        return {'success': False, 'error': 'Đã xảy ra lỗi khi cập nhật trạng thái'}


def handle_delete_user(request):
    """Xử lý xóa user"""
    try:
        target_username = request.POST.get("target_username")
        
        result = UserService.delete_user(target_username, request.user)
        
        if result['success']:
            result['message'] = f"Đã xóa tài khoản {target_username} thành công."
        
        return result
        
    except Exception as e:
        logger.error(f"Error in handle_delete_user: {str(e)}")
        return {'success': False, 'error': 'Đã xảy ra lỗi khi xóa user'}


@login_required
def change_password_view(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Mật khẩu không khớp!")
            return redirect('home')
        
        if len(new_password) < 6:
            messages.error(request, "Mật khẩu phải có ít nhất 6 ký tự!")
            return redirect('home')
        
        try:
            user = request.user
            user.set_password(new_password)
            user.is_password_changed = True
            user.password_reset_required = False
            user.save()
            update_session_auth_hash(request, user)
            
            logger.info(f"User {user.username} changed password")
            messages.success(request, "Đổi mật khẩu thành công!")
            
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            messages.error(request, "Đã xảy ra lỗi. Vui lòng thử lại!")
        
        return redirect('home')
        
    return redirect('home')
