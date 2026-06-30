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
from .models import CustomUser
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils import timezone 
from .models import UserActivityLog
from django.db.models.functions import TruncDate
from django.db.models import Count
def home(request):
    # Nếu người dùng chưa đăng nhập, bắt buộc đá về trang login trước
    if not request.user.is_authenticated:
        return redirect('login')  # Đổi từ 'login_view' thành 'login' cho ngắn gọn và chuẩn
    
    # Nếu đã đăng nhập rồi thì tùy theo quyền mà trả về giao diện đúng
    return render_by_role(request, request.user)

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') # Lấy checkbox từ HTML

        user = authenticate(request, username=email, password=password)
        
        if user is None:
            # Dùng context để gửi thông báo lỗi ra template
            return render(request, 'coreapp/login.html', {'error_message': "Sai email hoặc mật khẩu!"})
        
        # Đăng nhập thành công
        login(request, user)

        write_log(request, "Đã đăng nhập hệ thống")
        # XỬ LÝ GHI NHỚ ĐĂNG NHẬP
        if remember_me:
            # Lưu session trong 2 tuần (14 ngày)
            request.session.set_expiry(1209600) 
        else:
            # Đóng session khi tắt trình duyệt
            request.session.set_expiry(0) 
            
        return render_by_role(request, user)

    return render(request, 'coreapp/login.html')

def logout_view(request):
    write_log(request, "Đã đăng xuất hệ thống")
    logout(request)
    return redirect('/login/')

def render_by_role(request, user):
    # 1. Nếu là Admin
    if user.role == 'ADMIN' or user.is_staff:
        return redirect('admin_dashboard') 
        
    # 2. Nếu là User thường
    if user.role == 'USER':
        return render(request, 'user/home.html') # Hoặc trang chủ của User
        
    # 3. Mặc định nếu không thuộc role nào
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
        print("Đã nhận được POST request:", request.POST)
        action_type = request.POST.get("action_type")
        target_username = request.POST.get("target_username")
        
        # --- THAO TÁC: TẠO TÀI KHOẢN ---
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
                
                # 1. Tạo user
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
                if role == 'ADMIN':
                    user.is_staff = True      # Tự động tick vào ô Staff status
                    user.is_superuser = False # Đảm bảo không phải là superuser
                    user.save()
                # 2. GÁN NHÓM (CỰC KỲ QUAN TRỌNG)
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
    
                # 3. Lưu dữ liệu
                user.plain_password_temp = pwd
                user.save()
                write_log(request, f"Đã tạo tài khoản tên là {username}")
                messages.success(request, f"Tạo tài khoản {username} thành công.")

        # --- THAO TÁC: RESET MẬT KHẨU ---
        elif action_type == "reset_password":
            new_pwd = request.POST.get("new_password", "").strip()
            if not new_pwd: new_pwd = generate_secure_random_password()
            try:
                user = User.objects.get(username=target_username)
                user.set_password(new_pwd)
                user.plain_password_temp = new_pwd # LƯU VÀO DB
                user.is_password_changed = False
                user.save()
                write_log(request, f"Đã reset mật khẩu cho {target_username}")
                messages.success(request, f"Đã reset mật khẩu cho {target_username}")
            except User.DoesNotExist:
                messages.error(request, "Không tìm thấy user.")

        # --- THAO TÁC: KHÓA/MỞ TÀI KHOẢN ---
        elif action_type == "toggle_status":
            current_status = request.POST.get("current_status")  # Nhận vào "lock" hoặc "unlock" từ JS
            try:
                user = User.objects.get(username=target_username)
                
                if current_status == "lock":
                    user.is_active = False
                    user.save()
                    # GHI LOG HÀNH ĐỘNG KHÓA
                    write_log(request, f"Đã đình chỉ (KHÓA) tài khoản nhân sự: {target_username}")
                    messages.success(request, f"Đã khóa tài khoản {target_username} thành công.")
                else:
                    user.is_active = True
                    user.save()
                    # GHI LOG HÀNH ĐỘNG MỞ KHÓA
                    write_log(request, f"Đã kích hoạt lại (MỞ KHÓA) tài khoản nhân sự: {target_username}")
                    messages.success(request, f"Đã mở khóa tài khoản {target_username} thành công.")
                    
            except User.DoesNotExist:
                messages.error(request, "Lỗi cập nhật trạng thái user: Tài khoản không tồn tại.")
        elif action_type == "delete_user":
            try:
                # Tìm user theo username
                user_to_delete = User.objects.get(username=target_username)
                
                # Kiểm tra an toàn: Không cho phép Admin xóa chính mình
                if user_to_delete == request.user:
                    messages.error(request, "Bạn không thể tự xóa tài khoản của chính mình!")
                else:
                    user_to_delete.delete()
                    write_log(request, f"Đã xóa tài khoản {target_username}")
                    messages.success(request, f"Đã xóa tài khoản {target_username} thành công.")
            except User.DoesNotExist:
                messages.error(request, "Tài khoản không tồn tại.")
            return redirect('admin_dashboard')

        return redirect('admin_dashboard')   
    # Lấy toàn bộ user để hiển thị bảng
    all_users = User.objects.all().order_by('-date_joined')
    
    # Lọc người dùng theo Role đã lưu trong DB (hoặc theo Group)
    user_accounts = User.objects.filter(role='USER')
    admin_accounts = User.objects.filter(role='ADMIN')
    query = request.GET.get('q', '').strip()
    phone = request.GET.get('phone_filter', '').strip()
    birth = request.GET.get('birth_filter', '').strip()
    status = request.GET.get('status', '')

    # 1. Bắt đầu với tất cả user
    users = User.objects.all().order_by('-date_joined')

    # 2. Áp dụng các bộ lọc nếu có
    if query:
        users = users.filter(
            Q(username__icontains=query) | Q(email__icontains=query) |
            Q(phone_number__icontains=query) | Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    if phone:
        users = users.filter(phone_number__icontains=phone)
    if birth:
        users = users.filter(birth_date=birth)
    if status:
        users = users.filter(is_active=(status == '1'))

    context = {
        'all_users': all_users,
        'user_accounts': user_accounts, 
        'admin_accounts': admin_accounts,
    }
    return render(request, 'admin/total.html', context)

def change_password_view(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password') # Sửa ở đây
        
        # Kiểm tra trùng khớp
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

def user(request):
    # BỔ SUNG: Nếu bấm nút thao tác (Khóa, Mở, Reset, Xóa), chuyển tiếp dữ liệu qua hàm admin_dashboard xử lý
    if request.method == "POST":
        return admin_dashboard(request)

    # 1. Lấy danh sách user theo role 'USER'
    users = get_filtered_users(request).filter(role='USER').order_by('-date_joined')
    
    # 2. Thiết lập phân trang (5 user mỗi trang)
    paginator = Paginator(users, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 3. Render với tên biến 'user_accounts' như cũ
    return render(request, "admin/user.html", {'user_accounts': page_obj})

def adminqt(request):
    # BỔ SUNG: Nếu bấm nút thao tác (Khóa, Mở, Reset, Xóa), chuyển tiếp dữ liệu qua hàm admin_dashboard xử lý
    if request.method == "POST":
        return admin_dashboard(request)

    # 1. Lấy danh sách admin và sắp xếp thứ tự
    users = get_filtered_users(request).filter(role='ADMIN').order_by('-date_joined')
    
    # 2. Thiết lập phân trang
    paginator = Paginator(users, 5) # 5 admin mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 3. Render với tên biến 'admin_accounts'
    return render(request, "admin/adminqt.html", {'admin_accounts': page_obj})

def total(request):
    # BỔ SUNG: Nếu bấm nút thao tác (Khóa, Mở, Reset, Xóa), chuyển tiếp dữ liệu qua hàm admin_dashboard xử lý
    if request.method == "POST":
        return admin_dashboard(request)

    # 1. Lấy danh sách user từ hàm cũ của bạn
    users = get_filtered_users(request).order_by('-date_joined')
    
    # 2. CHÈN PHÂN TRANG VÀO ĐÂY
    paginator = Paginator(users, 5) # Chia mỗi trang 5 user
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 3. Truyền 'page_obj' vào template thay vì 'users'
    # Lưu ý: Trong template, bạn vẫn dùng biến tên là 'all_users'
    return render(request, "admin/total.html", {'all_users': page_obj})

def get_filtered_users(request):
    """Hàm hỗ trợ lọc dùng chung cho mọi trang"""
    query = request.GET.get('q', '').strip()
    phone = request.GET.get('phone_filter', '').strip()
    birth = request.GET.get('birth_filter', '').strip()
    status = request.GET.get('status', '')

    users = User.objects.all().order_by('-date_joined')
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    if phone:
        users = users.filter(phone_number__icontains=phone)
    if status:
        users = users.filter(is_active=(status == '1'))
    return users

def total(request):
    # 1. Lấy danh sách user từ hàm cũ của bạn
    users = get_filtered_users(request).order_by('-date_joined')
    
    # 2. CHÈN PHÂN TRANG VÀO ĐÂY
    paginator = Paginator(users, 5) # Chia mỗi trang 5 user
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 3. Truyền 'page_obj' vào template thay vì 'users'
    # Lưu ý: Trong template, bạn vẫn dùng biến tên là 'all_users'
    return render(request, "admin/total.html", {'all_users': page_obj})

def user(request):
    # 1. Lấy danh sách user theo role 'USER'
    users = get_filtered_users(request).filter(role='USER').order_by('-date_joined')
    
    # 2. Thiết lập phân trang (5 user mỗi trang)
    paginator = Paginator(users, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 3. Render với tên biến 'user_accounts' như cũ
    return render(request, "admin/user.html", {'user_accounts': page_obj})

def adminqt(request):
    # 1. Lấy danh sách admin và sắp xếp thứ tự
    users = get_filtered_users(request).filter(role='ADMIN').order_by('-date_joined')
    
    # 2. Thiết lập phân trang
    paginator = Paginator(users, 5) # 5 admin mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 3. Render với tên biến 'admin_accounts'
    return render(request, "admin/adminqt.html", {'admin_accounts': page_obj})
@login_required
def log_today_view(request):
    today_vn = timezone.localdate()
    
    # SỬA LOGIC: Kiểm tra role 'ADMIN' HOẶC 'is_staff'
    is_admin_or_staff = (request.user.role == 'ADMIN' or request.user.is_staff)
    
    if is_admin_or_staff:
        # Lấy tất cả log
        logs = UserActivityLog.objects.filter(timestamp__date=today_vn).order_by('timestamp')
    else:
        # Chỉ lấy log của chính user đó
        logs = UserActivityLog.objects.filter(user=request.user, timestamp__date=today_vn).order_by('timestamp')
        
    return render(request, 'admin/log_today.html', {'logs': logs})

@login_required
def log_all_view(request):
    # Logic tương tự cho log lịch sử
    queryset = UserActivityLog.objects.all() if request.user.is_staff else UserActivityLog.objects.filter(user=request.user)
    
    logs_by_date = (
        queryset.annotate(date_only=TruncDate('timestamp'))
        .values('date_only')
        .annotate(total_logs=Count('id'))
        .order_by('-date_only')
    )
    
    return render(request, 'admin/log_all.html', {'logs_by_date': logs_by_date})

@login_required
def log_detail_view(request, date_str):
    """Xem chi tiết log của một ngày cụ thể"""
    
    # SỬA Ở ĐÂY: Dùng is_staff để đồng bộ với các hàm khác
    if request.user.is_staff:
        # Admin/Staff thấy toàn bộ log của tất cả mọi người
        logs = UserActivityLog.objects.filter(timestamp__date=date_str).select_related('user').order_by('timestamp')
    else:
        # User thường chỉ thấy log của chính họ
        logs = UserActivityLog.objects.filter(user=request.user, timestamp__date=date_str).select_related('user').order_by('timestamp')
        
    context = {
        'date_str': date_str,
        'logs': logs
    }
    return render(request, 'admin/log_detail.html', context)

def write_log(request, action_text):
    """Hàm bổ trợ giúp ghi log nhanh bằng 1 dòng code"""
    # Lấy IP của người dùng thực hiện
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    
    # Ghi vào Database
    UserActivityLog.objects.create(
        user=request.user,
        action=action_text,
        path=request.path,
        ip_address=ip,
        timestamp=timezone.now()
    )
