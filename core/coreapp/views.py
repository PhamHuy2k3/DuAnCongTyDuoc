from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db.models import Q
import logging

from .services import UserService, log_action
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
                log_action(request, 'LOGIN_FAILED', target_type='User',
                           target_label=email,
                           detail={'email': email, 'reason': 'Sai email hoặc mật khẩu'})
                return render(request, 'coreapp/login.html', {
                    'error_message': "Sai email hoặc mật khẩu!"
                })
            
            if not user.is_active:
                logger.warning(f"Inactive user login attempt: {email}")
                return render(request, 'coreapp/login.html', {
                    'error_message': "Tài khoản của bạn đã bị khóa!"
                })
            
            login(request, user)
            log_action(request, 'LOGIN', target_type='User',
                       target_id=user.id, target_label=user.username,
                       detail={'email': user.email, 'role': user.role})
            
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
    user_id = request.user.id if request.user.is_authenticated else None
    log_action(request, 'LOGOUT', target_type='User',
               target_id=user_id, target_label=username)
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

            elif action_type == "delete_doc":
                from user.models import ScannedDocument
                doc_id = request.POST.get('target_id')
                try:
                    doc = ScannedDocument.objects.get(id=doc_id)
                    doc_name = doc.file_name
                    doc.delete()
                    log_action(request, 'DOC_REJECTED', target_type='ScannedDocument', target_label=doc_name, detail={'deleted_by_admin': True})
                    messages.success(request, f"Đã xóa tài liệu {doc_name} thành công.")
                except ScannedDocument.DoesNotExist:
                    messages.error(request, "Tài liệu không tồn tại.")

            elif action_type == "delete_med":
                from user.models import MedicineItem
                med_id = request.POST.get('target_id')
                try:
                    med = MedicineItem.objects.get(id=med_id)
                    med_name = med.trade_name
                    med.delete()
                    log_action(request, 'MEDICINE_DELETED', target_type='MedicineItem', target_label=med_name, detail={'deleted_by_admin': True})
                    messages.success(request, f"Đã xóa dược phẩm {med_name} thành công.")
                except MedicineItem.DoesNotExist:
                    messages.error(request, "Dược phẩm không tồn tại.")

                    
        except Exception as e:
            logger.error(f"Admin dashboard error: {str(e)}")
            messages.error(request, "Đã xảy ra lỗi. Vui lòng thử lại!")
        
        return redirect('admin_dashboard')
    
    # GET request
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from coreapp.models import SystemLog
        from user.models import ScannedDocument, MedicineItem
        from django.utils import timezone
        import datetime
        import json
        
        all_users = User.objects.select_related().order_by('-date_joined')
        user_accounts = all_users.filter(role='USER')
        admin_accounts = all_users.filter(role='ADMIN')
        
        system_logs = SystemLog.objects.select_related('actor').all()[:300]
        
        all_documents = ScannedDocument.objects.select_related('user', 'medicine', 'reviewed_by').all()

        # Analytics Metrics
        total_users = user_accounts.count()
        total_docs = all_documents.count()
        approved_docs = all_documents.filter(status='approved').count()
        pending_docs = all_documents.filter(status='pending').count()
        
        # 7-day Chart Data
        today = timezone.now().date()
        dates = [(today - datetime.timedelta(days=i)).strftime('%d/%m') for i in range(6, -1, -1)]
        
        scans_by_day = []
        for i in range(6, -1, -1):
            day_start = timezone.make_aware(datetime.datetime.combine(today - datetime.timedelta(days=i), datetime.time.min))
            day_end = timezone.make_aware(datetime.datetime.combine(today - datetime.timedelta(days=i), datetime.time.max))
            count = all_documents.filter(scanned_at__range=(day_start, day_end)).count()
            scans_by_day.append(count)

        context = {
            'all_users': all_users,
            'user_accounts': user_accounts,
            'admin_accounts': admin_accounts,
            'system_logs': system_logs,
            'all_documents': all_documents,
            'metrics': {
                'total_users': total_users,
                'total_docs': total_docs,
                'approved_docs': approved_docs,
                'pending_docs': pending_docs,
            },
            'chart_labels': json.dumps(dates),
            'chart_data': json.dumps(scans_by_day)
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
            created_user = result.get('user')
            log_action(request, 'USER_CREATED', target_type='User',
                       target_id=created_user.id if created_user else None,
                       target_label=username,
                       detail={
                           'email': email,
                           'fullname': fullname,
                           'role': role,
                           'birth_date': birth_date or '',
                           'phone_number': phone_number or '',
                       })
        
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
            log_action(request, 'PASSWORD_RESET', target_type='User',
                       target_label=target_username,
                       detail={
                           'reset_by': request.user.username,
                           'method': 'Mật khẩu tự đặt' if new_password else 'Tạo ngẫu nhiên',
                       })
        
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
            is_locking = (current_status == 'lock')
            action = 'USER_LOCKED' if is_locking else 'USER_UNLOCKED'
            toggled_user = result.get('user')
            log_action(request, action, target_type='User',
                       target_id=toggled_user.id if toggled_user else None,
                       target_label=target_username,
                       detail={
                           'old_status': 'Đang hoạt động' if is_locking else 'Đang khóa',
                           'new_status': 'Đang khóa' if is_locking else 'Đang hoạt động',
                           'changed_by': request.user.username,
                       })
            result['message'] = f"Đã cập nhật trạng thái cho {target_username}"
        
        return result
        
    except Exception as e:
        logger.error(f"Error in handle_toggle_status: {str(e)}")
        return {'success': False, 'error': 'Đã xảy ra lỗi khi cập nhật trạng thái'}


def handle_delete_user(request):
    """Xử lý xóa user"""
    try:
        target_username = request.POST.get("target_username")
        
        # Lưu thông tin user trước khi xóa (vì sau khi xóa sẽ mất)
        from django.contrib.auth import get_user_model
        _User = get_user_model()
        try:
            _target = _User.objects.get(username=target_username)
            _deleted_info = {
                'email': _target.email,
                'role': _target.role,
                'fullname': _target.get_full_name(),
                'deleted_by': request.user.username,
            }
        except _User.DoesNotExist:
            _deleted_info = {'deleted_by': request.user.username}
        
        result = UserService.delete_user(target_username, request.user)
        
        if result['success']:
            log_action(request, 'USER_DELETED', target_type='User',
                       target_label=target_username,
                       detail=_deleted_info)
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
            log_action(request, 'PASSWORD_CHANGED', target_type='User',
                       target_id=user.id, target_label=user.username,
                       detail={'changed_by_self': True})
            messages.success(request, "Đổi mật khẩu thành công!")
            
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            messages.error(request, "Đã xảy ra lỗi. Vui lòng thử lại!")
        
        return redirect('home')
        
    return redirect('home')

@login_required
@user_passes_test(is_admin, login_url='login')
def log_detail_api(request, log_id):
    """API trả về thông tin chi tiết của một dòng SystemLog"""
    from coreapp.models import SystemLog
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404
    
    log_entry = get_object_or_404(SystemLog, id=log_id)
    actor_name = log_entry.actor.username if log_entry.actor else 'Hệ thống'
    
    return JsonResponse({
        'success': True,
        'log': {
            'id': log_entry.id,
            'timestamp': log_entry.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
            'actor': actor_name,
            'action': log_entry.get_action_display(),
            'action_code': log_entry.action,
            'target_type': log_entry.target_type,
            'target_label': log_entry.target_label,
            'ip_address': log_entry.ip_address,
            'detail': log_entry.detail
        }
    })
