from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import ScannedDocument, MedicineItem
import json
import os
import re


def home(request):
    return render(request, 'user/home.html')


def scan_demo(request):
    return render(request, 'user/scan.html')


def login_view(request):
    return render(request, 'user/login.html')


def register_view(request):
    return render(request, 'user/register.html')


@login_required(login_url='login')
def dashboard_view(request):
    docs = ScannedDocument.objects.filter(user=request.user)
    medicines = MedicineItem.objects.filter(
        scanneddocument__user=request.user
    ).distinct()

    total_scans = docs.count()
    pending_count = docs.filter(status='pending').count()
    approved_count = docs.filter(status='approved').count()
    rejected_count = docs.filter(status='rejected').count()

    latest_docs = docs.order_by('-scanned_at')[:10]
    pending_docs = docs.filter(status='pending').order_by('-scanned_at')
    approved_medicines = MedicineItem.objects.filter(
        scanneddocument__user=request.user,
        scanneddocument__status='approved'
    ).distinct().order_by('-created_at')

    avg_accuracy = 0
    if total_scans > 0:
        avg_accuracy = docs.filter(accuracy_score__gt=0).aggregate(Avg('accuracy_score'))['accuracy_score__avg'] or 0
        avg_accuracy = round(avg_accuracy, 1)

    context = {
        'total_scans': total_scans,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'avg_accuracy': avg_accuracy,
        'latest_docs': latest_docs,
        'pending_docs': pending_docs,
        'approved_medicines': approved_medicines,
    }
    return render(request, 'user/dashboard.html', context)


@login_required(login_url='login')
def approve_document(request, doc_id):
    if request.method == 'POST':
        doc = get_object_or_404(ScannedDocument, id=doc_id, user=request.user, status='pending')
        doc.status = 'approved'
        doc.reviewed_by = request.user
        doc.reviewed_at = timezone.now()
        doc.save()
        if doc.medicine:
            med = doc.medicine
            med.approved_by = request.user
            med.approved_at = timezone.now()
            med.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required(login_url='login')
def reject_document(request, doc_id):
    if request.method == 'POST':
        doc = get_object_or_404(ScannedDocument, id=doc_id, user=request.user, status='pending')
        doc.status = 'rejected'
        doc.reviewed_by = request.user
        doc.reviewed_at = timezone.now()
        doc.notes = request.POST.get('notes', '')
        doc.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)


@login_required(login_url='login')
def dashboard_stats(request):
    docs = ScannedDocument.objects.filter(user=request.user)
    medicines = MedicineItem.objects.filter(scanneddocument__user=request.user)
    total = docs.count()
    return JsonResponse({
        'total_scans': total,
        'pending': docs.filter(status='pending').count(),
        'approved': docs.filter(status='approved').count(),
        'rejected': docs.filter(status='rejected').count(),
        'medicines_count': medicines.count(),
    })


@login_required(login_url='login')
def profile_view(request):
    user = request.user
    docs = ScannedDocument.objects.filter(user=user)
    medicines_count = MedicineItem.objects.filter(scanneddocument__user=user).distinct().count()

    total_scans = docs.count()
    recent_activity = docs.order_by('-scanned_at')[:5]

    stats = {
        'total_scans': total_scans,
        'pending': docs.filter(status='pending').count(),
        'approved': docs.filter(status='approved').count(),
        'rejected': docs.filter(status='rejected').count(),
        'medicines_count': medicines_count,
    }

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.phone_number = request.POST.get('phone_number', user.phone_number)
            birth_date = request.POST.get('birth_date')
            if birth_date:
                from datetime import datetime
                try:
                    user.birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            user.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('profile')

        elif action == 'change_password':
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if not user.check_password(current_password):
                messages.error(request, 'Mật khẩu hiện tại không đúng!')
            elif len(new_password) < 6:
                messages.error(request, 'Mật khẩu mới phải có ít nhất 6 ký tự!')
            elif new_password != confirm_password:
                messages.error(request, 'Mật khẩu mới không khớp!')
            else:
                user.set_password(new_password)
                user.is_password_changed = True
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Đổi mật khẩu thành công!')
            return redirect('profile')

        elif action == 'update_avatar':
            pass

    context = {
        'stats': stats,
        'recent_activity': recent_activity,
        'total_scans': total_scans,
        'medicines_count': medicines_count,
    }
    return render(request, 'user/profile.html', context)


def coa_view(request):
    from django.http import HttpResponse

    form1_path = os.path.join(os.path.dirname(__file__), 'templates', 'user', 'form1.html')
    with open(form1_path, 'r', encoding='utf-8') as f:
        form1_content = f.read()

    match = re.search(
        r'(<div id="pf1" class="pf w0 h0" data-page-no="1">.*?<div class="pi" data-data=[^>]*?></div></div>)',
        form1_content,
        re.DOTALL
    )
    if match:
        page_html = match.group(1)
        pages = []
        for i in range(1, 21):
            p = page_html.replace('id="pf1"', f'id="pf{i}"')
            p = p.replace('data-page-no="1"', f'data-page-no="{i}"')
            p = p.replace('pc1', f'pc{i}')
            pages.append(p)

        multi_pages_html = '\n'.join(pages)
        form1_content = form1_content.replace(page_html, multi_pages_html)

    return HttpResponse(form1_content)