from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
import string
import secrets
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render_by_role(request, request.user)

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return render(request, 'coreapp/login.html', {'error_message': "Sai email hoặc mật khẩu!"})
        
        login(request, user)
        
        if remember_me:
            request.session.set_expiry(1209600) 
        else:
            request.session.set_expiry(0) 
            
        return render_by_role(request, user)

    return render(request, 'coreapp/login.html')

def logout_view(request):
    logout(request)
    return redirect('/login/')

def render_by_role(request, user):
    if user.role == 'ADMIN' or user.is_staff:
        return redirect('admin_dashboard') 
        
    if user.role == 'USER':
        return render(request, 'user/home.html')
        
    logout(request)
    messages.error(request, "Tài khoản của bạn chưa được phân quyền truy cập.")
    return redirect('login')

User = get_user_model()

def generate_secure_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + "@#$%"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@login_required
@user_passes_test(lambda u: u.is_staff or getattr(u, 'role', '') == 'ADMIN', login_url='login')
def admin_dashboard(request):
    if request.method == "POST":
        action_type = request.POST.get("action_type")
        target_username = request.POST.get("target_username")
        
        if action_type == "create_user":
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip()
            fullname = request.POST.get("fullname", "").strip()
            role = request.POST.get("role")
            birth_date = request.POST.get("birth_date")
            phone_number = request.POST.get("phone_number")
            is_password_changed=False
            if User.objects.filter(username=username).exists():
                messages.error(request, f"Tên đăng nhập '{username}' đã tồn tại!")
            elif User.objects.filter(email=email).exists():
                messages.error(request, f"Email '{email}' đã tồn tại!")
            else:
                pwd = generate_secure_random_password()
                name_parts = fullname.split(' ', 1)
                
                user = User.objects.create_user(
                    username=username, 
                    email=email, 
                    password=pwd,
                    first_name=name_parts[1] if len(name_parts) > 1 else name_parts[0],
                    last_name=name_parts[0] if len(name_parts) > 1 else "",
                    role=role,
                    birth_date=birth_date,     
                    phone_number=phone_number,
                    is_password_changed=False
                )
                
                group_map = {
                    'USER': 'USER',
                    'ADMIN': 'ADMIN'
                }
                
                target_group_name = group_map.get(role)
                if target_group_name:
                    try:
                        group = Group.objects.get(name=target_group_name)
                        user.groups.add(group)
                    except Group.DoesNotExist:
                        # Ghi log lỗi nếu bạn chưa tạo Group trong trang Admin
                        print(f"Lỗi: Nhóm '{target_group_name}' chưa được tạo trong DB!")

                user.plain_password_temp = pwd
                user.save()
                messages.success(request, f"Tạo tài khoản {username} thành công.")

        elif action_type == "reset_password":
            new_pwd = request.POST.get("new_password", "").strip()
            if not new_pwd: new_pwd = generate_secure_random_password()
            try:
                user = User.objects.get(username=target_username)
                user.set_password(new_pwd)
                user.plain_password_temp = new_pwd
                user.is_password_changed = False
                user.save()
                messages.success(request, f"Đã reset mật khẩu cho {target_username}")
            except User.DoesNotExist:
                messages.error(request, "Không tìm thấy user.")

        elif action_type == "toggle_status":
            current_status = request.POST.get("current_status")
            try:
                user = User.objects.get(username=target_username)
                user.is_active = (current_status != "lock")
                user.save()
                messages.success(request, f"Đã cập nhật trạng thái cho {target_username}")
            except User.DoesNotExist:
                messages.error(request, "Lỗi cập nhật user.")
        elif action_type == "delete_user":
            try:
                user_to_delete = User.objects.get(username=target_username)
                
                if user_to_delete == request.user:
                    messages.error(request, "Bạn không thể tự xóa tài khoản của chính mình!")
                else:
                    user_to_delete.delete()
                    messages.success(request, f"Đã xóa tài khoản {target_username} thành công.")
            except User.DoesNotExist:
                messages.error(request, "Tài khoản không tồn tại.")
            return redirect('admin_dashboard')

        return redirect('admin_dashboard')
    all_users = User.objects.all().order_by('-date_joined')
    
    user_accounts = User.objects.filter(role='USER')
    admin_accounts = User.objects.filter(role='ADMIN')

    context = {
        'all_users': all_users,
        'user_accounts': user_accounts,
        'admin_accounts': admin_accounts,
    }
    return render(request, 'admin/admin.html', context)

def change_password_view(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password: 
            messages.error(request, "Mật khẩu không khớp!")
            return redirect('home')

        user = request.user
        user.set_password(new_password)
        user.is_password_changed = True
        user.save()
        update_session_auth_hash(request, user)
        
        messages.success(request, "Đổi mật khẩu thành công!")
        return redirect('home')
    return redirect('home')