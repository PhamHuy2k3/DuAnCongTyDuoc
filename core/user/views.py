from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from .models import ScannedDocument, MedicineItem, WeightUniformityRecord, SavedCOAReport
from .services import process_image, validate_image_file, extract_balance_receipt_records
import json
import os
import re
import logging
from datetime import datetime
from django.db.models import Avg
from coreapp.services import log_action

logger = logging.getLogger('user')


def home(request):
    return render(request, 'user/home.html')


def scan_demo(request):
    fields = [
        {'name': 'trade_name', 'label': 'Tên thương mại', 'required': True},
        {'name': 'active_ingredient', 'label': 'Hoạt chất chính', 'required': True},
        {'name': 'strength', 'label': 'Hàm lượng / Nồng độ', 'required': False},
        {'name': 'dosage_form', 'label': 'Dạng bào chế', 'required': False},
        {'name': 'manufacturer', 'label': 'Nhà sản xuất', 'required': True},
        {'name': 'batch_number', 'label': 'Số lô sản xuất', 'required': True},
        {'name': 'registration_number', 'label': 'Số đăng ký lưu hành', 'required': False},
        {'name': 'mfg_date', 'label': 'Ngày sản xuất', 'required': False},
        {'name': 'exp_date', 'label': 'Hạn sử dụng', 'required': True},
        {'name': 'indications', 'label': 'Chỉ định điều trị', 'required': False},
    ]
    return render(request, 'user/scan.html', {'fields': fields})


@login_required(login_url='login')
def upload_document(request):
    if request.method != 'POST':
        logger.warning(f"Invalid method {request.method} for upload_document")
        return JsonResponse({'success': False, 'error': 'Chỉ hỗ trợ phương thức POST'}, status=405)

    if 'file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'Vui lòng chọn file để tải lên'}, status=400)

    uploaded_file = request.FILES['file']

    try:
        # Validate image file
        validate_image_file(uploaded_file)
        
        # Save file
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', str(request.user.id))
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, 'wb+') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # Process image với OCR
        extracted = process_image(file_path)
        
        # Create Medicine record
        medicine = MedicineItem.objects.create(
            trade_name=extracted['data'].get('trade_name', ''),
            active_ingredient=extracted['data'].get('active_ingredient', ''),
            strength=extracted['data'].get('strength', ''),
            dosage_form=extracted['data'].get('dosage_form', ''),
            manufacturer=extracted['data'].get('manufacturer', ''),
            batch_number=extracted['data'].get('batch_number', ''),
            registration_number=extracted['data'].get('registration_number', ''),
            mfg_date=extracted['data'].get('mfg_date', ''),
            exp_date=extracted['data'].get('exp_date', ''),
            indications=extracted['data'].get('indications', ''),
        )

        # Create ScannedDocument record
        doc = ScannedDocument.objects.create(
            user=request.user,
            medicine=medicine,
            file_name=uploaded_file.name,
            accuracy_score=extracted['accuracy'],
            status='pending',
        )
        
        logger.info(f"User {request.user.username} uploaded image {uploaded_file.name}, OCR engine: {extracted.get('ocr_engine')}")

        return JsonResponse({
            'success': True,
            'doc_id': doc.id,
            'data': extracted['data'],
            'accuracy': extracted['accuracy'],
            'ocr_engine': extracted.get('ocr_engine', 'unknown'),
            'message': 'Quét ảnh thành công!'
        })
        
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Lỗi xử lý ảnh: {str(e)}'}, status=500)


def login_view(request):
    return render(request, 'user/login.html')


def register_view(request):
    return render(request, 'user/register.html')


@login_required(login_url='login')
def dashboard_view(request):
    try:
        docs = ScannedDocument.objects.filter(user=request.user).select_related('medicine', 'reviewed_by')
        medicines = MedicineItem.objects.filter(
            scanneddocument__user=request.user
        ).distinct()

        total_scans = docs.count()
        pending_count = docs.filter(status='pending').count()
        approved_count = docs.filter(status='approved').count()
        rejected_count = docs.filter(status='rejected').count()

        latest_docs = docs.order_by('-scanned_at')[:10]
        pending_docs = docs.filter(status='pending').order_by('-scanned_at')[:20]
        approved_medicines = MedicineItem.objects.filter(
            scanneddocument__user=request.user,
            scanneddocument__status='approved'
        ).distinct().order_by('-created_at')[:20]

        avg_accuracy = 0
        if total_scans > 0:
            avg_accuracy = docs.filter(accuracy_score__gt=0).aggregate(Avg('accuracy_score'))['accuracy_score__avg'] or 0
            avg_accuracy = round(avg_accuracy, 1)

        saved_reports = SavedCOAReport.objects.filter(user=request.user).order_by('-saved_at')

        context = {
            'total_scans': total_scans,
            'pending_count': pending_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'avg_accuracy': avg_accuracy,
            'latest_docs': latest_docs,
            'pending_docs': pending_docs,
            'approved_medicines': approved_medicines,
            'saved_reports': saved_reports,
        }
        return render(request, 'user/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        messages.error(request, "Không thể tải dữ liệu dashboard")
        return render(request, 'user/dashboard.html', {})


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
            
        log_action(request, 'DOC_APPROVED', target_type='Document',
                   target_id=doc.id, target_label=doc.file_name,
                   detail={'reviewed_by': request.user.username})
                   
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
        
        log_action(request, 'DOC_REJECTED', target_type='Document',
                   target_id=doc.id, target_label=doc.file_name,
                   detail={'reviewed_by': request.user.username, 'notes': doc.notes})
                   
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
            log_action(request, 'PROFILE_UPDATED', target_type='User', target_label=user.username, target_id=user.id)
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


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD CRUD ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def document_detail(request, doc_id):
    """Trả về chi tiết 1 ScannedDocument dưới dạng JSON."""
    doc = get_object_or_404(ScannedDocument, id=doc_id, user=request.user)
    med = doc.medicine
    return JsonResponse({
        'success': True,
        'doc': {
            'id': doc.id,
            'file_name': doc.file_name,
            'scanned_at': doc.scanned_at.strftime('%d/%m/%Y %H:%M'),
            'status': doc.status,
            'status_display': doc.get_status_display(),
            'accuracy_score': doc.accuracy_score,
            'notes': doc.notes,
            'reviewed_by': doc.reviewed_by.get_full_name() if doc.reviewed_by else '',
            'reviewed_at': doc.reviewed_at.strftime('%d/%m/%Y %H:%M') if doc.reviewed_at else '',
            'medicine': {
                'id': med.id,
                'trade_name': med.trade_name,
                'active_ingredient': med.active_ingredient,
                'strength': med.strength,
                'dosage_form': med.dosage_form,
                'manufacturer': med.manufacturer,
                'batch_number': med.batch_number,
                'registration_number': med.registration_number,
                'mfg_date': med.mfg_date,
                'exp_date': med.exp_date,
                'indications': med.indications,
            } if med else None,
        }
    })


@login_required(login_url='login')
def delete_document(request, doc_id):
    """Xóa một ScannedDocument (và MedicineItem liên quan)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Chỉ hỗ trợ POST'}, status=405)
    doc = get_object_or_404(ScannedDocument, id=doc_id, user=request.user)
    med = doc.medicine
    doc.delete()
    if med:
        med.delete()
    logger.info(f"User {request.user.username} deleted document {doc_id}")
    return JsonResponse({'success': True})


@login_required(login_url='login')
def medicine_list_api(request):
    """Trả về danh sách dược phẩm của user dưới dạng JSON (có search/filter)."""
    qs = MedicineItem.objects.filter(
        scanneddocument__user=request.user
    ).distinct().order_by('-created_at')

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(trade_name__icontains=search) |
            Q(active_ingredient__icontains=search) |
            Q(batch_number__icontains=search)
        )

    status_filter = request.GET.get('status', '')
    if status_filter in ('pending', 'approved', 'rejected'):
        qs = qs.filter(scanneddocument__status=status_filter)

    items = []
    for med in qs:
        doc = ScannedDocument.objects.filter(medicine=med).first()
        items.append({
            'id': med.id,
            'trade_name': med.trade_name,
            'active_ingredient': med.active_ingredient,
            'strength': med.strength,
            'dosage_form': med.dosage_form,
            'manufacturer': med.manufacturer,
            'batch_number': med.batch_number,
            'registration_number': med.registration_number,
            'mfg_date': med.mfg_date,
            'exp_date': med.exp_date,
            'indications': med.indications,
            'created_at': med.created_at.strftime('%d/%m/%Y'),
            'doc_id': doc.id if doc else None,
            'doc_status': doc.get_status_display() if doc else '',
            'doc_status_raw': doc.status if doc else '',
        })
    return JsonResponse({'success': True, 'items': items, 'total': len(items)})


@csrf_exempt
@login_required(login_url='login')
def medicine_create(request):
    """Tạo mới MedicineItem + ScannedDocument thủ công."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Chỉ hỗ trợ POST'}, status=405)
    try:
        body = json.loads(request.body)
        med = MedicineItem.objects.create(
            trade_name=body.get('trade_name', ''),
            active_ingredient=body.get('active_ingredient', ''),
            strength=body.get('strength', ''),
            dosage_form=body.get('dosage_form', ''),
            manufacturer=body.get('manufacturer', ''),
            batch_number=body.get('batch_number', ''),
            registration_number=body.get('registration_number', ''),
            mfg_date=body.get('mfg_date', ''),
            exp_date=body.get('exp_date', ''),
            indications=body.get('indications', ''),
        )
        doc = ScannedDocument.objects.create(
            user=request.user,
            medicine=med,
            file_name=f"[Nhập tay] {med.trade_name}",
            accuracy_score=100.0,
            status='approved',
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        med.approved_by = request.user
        med.approved_at = timezone.now()
        med.save()
        logger.info(f"User {request.user.username} manually created medicine {med.id}")
        log_action(request, 'MEDICINE_CREATED', target_type='MedicineItem', target_label=med.trade_name, target_id=med.id)
        return JsonResponse({'success': True, 'medicine_id': med.id, 'doc_id': doc.id})
    except Exception as e:
        logger.error(f"medicine_create error: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@login_required(login_url='login')
def medicine_update(request, med_id):
    """Cập nhật MedicineItem."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Chỉ hỗ trợ POST'}, status=405)
    # Chỉ cho phép sửa nếu medicine thuộc về doc của user
    med = get_object_or_404(
        MedicineItem,
        id=med_id,
        scanneddocument__user=request.user
    )
    try:
        body = json.loads(request.body)
        fields = ['trade_name', 'active_ingredient', 'strength', 'dosage_form',
                  'manufacturer', 'batch_number', 'registration_number',
                  'mfg_date', 'exp_date', 'indications']
        for f in fields:
            if f in body:
                setattr(med, f, body[f])
        med.save()
        logger.info(f"User {request.user.username} updated medicine {med_id}")
        log_action(request, 'MEDICINE_UPDATED', target_type='MedicineItem', target_label=med.trade_name, target_id=med.id)
        return JsonResponse({'success': True})
    except Exception as e:
        logger.error(f"medicine_update error: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='login')
def medicine_delete(request, med_id):
    """Xóa MedicineItem (và ScannedDocument liên quan)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Chỉ hỗ trợ POST'}, status=405)
    med = get_object_or_404(
        MedicineItem,
        id=med_id,
        scanneddocument__user=request.user
    )
    doc = ScannedDocument.objects.filter(medicine=med).first()
    if doc:
        doc.delete()
        
    _deleted_info = {
        'trade_name': med.trade_name,
        'batch_number': med.batch_number,
        'deleted_by': request.user.username
    }
    
    med.delete()
    logger.info(f"User {request.user.username} deleted medicine {med_id}")
    
    log_action(request, 'MEDICINE_DELETED', target_type='Medicine',
               target_label=_deleted_info['trade_name'],
               detail=_deleted_info)
               
    return JsonResponse({'success': True})


@login_required(login_url='login')
def document_list_api(request):
    """Trả về danh sách ScannedDocument của user dưới dạng JSON."""
    qs = ScannedDocument.objects.filter(user=request.user).select_related('medicine', 'reviewed_by').order_by('-scanned_at')

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            Q(file_name__icontains=search) |
            Q(medicine__trade_name__icontains=search)
        )

    status_filter = request.GET.get('status', '')
    if status_filter in ('pending', 'approved', 'rejected'):
        qs = qs.filter(status=status_filter)

    items = []
    for doc in qs:
        med = doc.medicine
        items.append({
            'id': doc.id,
            'file_name': doc.file_name,
            'scanned_at': doc.scanned_at.strftime('%d/%m/%Y %H:%M'),
            'status': doc.status,
            'status_display': doc.get_status_display(),
            'accuracy_score': doc.accuracy_score,
            'notes': doc.notes,
            'medicine_name': med.trade_name if med else '—',
            'batch_number': med.batch_number if med else '—',
        })
    return JsonResponse({'success': True, 'items': items, 'total': len(items)})


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


@csrf_exempt
@login_required(login_url='login')
def scan_receipt_api(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Chỉ hỗ trợ phương thức POST'}, status=405)
        
    if 'image' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'Vui lòng chọn file để tải lên'}, status=400)
        
    uploaded_file = request.FILES['image']
    
    try:
        from user.services import extract_balance_receipt_records, analyze_image_quality_with_ai
        
        # 1. AI Image Quality Filter (Dedicated AI model without text extraction to prevent hallucinations)
        uploaded_file.seek(0)
        quality_status = analyze_image_quality_with_ai(uploaded_file)
        
        if quality_status == 'unrelated':
            return JsonResponse({
                'success': False,
                'error_code': 'unrelated_image',
                'error': 'Hình ảnh không phù hợp, vui lòng chọn hình ảnh khác'
            }, status=400)
        elif quality_status == 'blurry':
            return JsonResponse({
                'success': False,
                'error_code': 'blurry_image',
                'error': 'Ảnh quá mờ để có thể trích xuất dữ liệu, vui lòng chọn ảnh rõ nét hơn.'
            }, status=400)
        elif quality_status == 'error':
            return JsonResponse({
                'success': False,
                'error_code': 'filter_error',
                'error': 'Hệ thống AI đang quá tải hoặc lỗi kết nối. Vui lòng thử lại sau vài giây.'
            }, status=400)
            
        # 2. Extract records via Gemini Vision API (Since image is clear)
        uploaded_file.seek(0)
        result = extract_balance_receipt_records(uploaded_file)

        # Handle validation error codes returned from Gemini (e.g. unrelated_image)
        if isinstance(result, dict) and 'error_code' in result:
            error_code = result['error_code']
            error_msg = result.get('error', 'Ảnh không hợp lệ.')
            if error_code in ['unrelated_image', 'invalid_image']:
                error_msg = 'Hình ảnh không phù hợp, vui lòng chọn hình ảnh khác'
            elif error_code == 'blurry_image':
                error_msg = 'Ảnh quá mờ để có thể trích xuất dữ liệu, vui lòng chọn ảnh rõ nét hơn.'
                
            return JsonResponse({
                'success': False,
                'error_code': error_code,
                'error': error_msg
            }, status=400)

        if not result:
            return JsonResponse({
                'success': False,
                'error': 'Không tìm thấy dữ liệu cân theo cấu trúc 2 cột trong ảnh. Vui lòng thử ảnh rõ hơn hoặc ảnh chụp trọn phiếu.'
            }, status=422)
        
        return JsonResponse({
            'success': True,
            'records': result
        })
        
    except Exception as e:
        logger.error(f"Error processing receipt vision OCR: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Lỗi hệ thống: {str(e)}'}, status=500)


@csrf_exempt
@login_required(login_url='login')
def generate_coa_from_scanned_data(request):
    """
    Generate COA HTML (Form 3 — Độ đồng đều khối lượng) dynamically from scanned weight records.
    Parses weight values in "0.256(1)" format, converts g→mg, calculates all pharmacopoeia stats.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Chỉ hỗ trợ phương thức POST'}, status=405)

    try:
        data = json.loads(request.body)
        records = data.get('records', [])
        drug_info = data.get('drug_info', {})

        if not records:
            return JsonResponse({'success': False, 'error': 'Không có dữ liệu để tạo COA'}, status=400)

        # ── Parse each record ──────────────────────────────────────────────
        def parse_weight_to_mg(raw):
            """
            Convert weight string to milligrams.
            Handles:  "0.256(1) g"  →  0.2561 g  →  256.1 mg
                      "0.256(1)"    →  0.2561 g  →  256.1 mg
                      "0.256 g"     →  0.256  g  →  256.0 mg
                      "256"         →  interpreted as mg directly (>=10 means mg)
            Returns float mg or None.
            """
            s = str(raw or '').strip()
            s = re.sub(r'\s*[gG]\s*$', '', s).strip()
            if not s or s == '-':
                return None

            # Format "0.256(1)"  →  base="0.256", extra="1"  →  "0.2561"
            m = re.match(r'^(\d+[.,]\d+)\((\d+)\)$', s)
            if m:
                base = m.group(1).replace(',', '.')
                extra = m.group(2)
                try:
                    val_g = float(base + extra)
                    return round(val_g * 1000, 4)
                except ValueError:
                    pass

            # Plain decimal "0.256" or "256.5"
            try:
                val = float(s.replace(',', '.'))
                # If value looks like grams (< 10), convert to mg; otherwise assume already mg
                if val < 10:
                    return round(val * 1000, 4)
                return round(val, 4)
            except ValueError:
                return None

        weights_mg = []
        parsed_records = []

        for idx, rec in enumerate(records, start=1):
            w_mg = parse_weight_to_mg(rec.get('weight', ''))
            if w_mg is not None:
                weights_mg.append(w_mg)

            parsed_records.append({
                'stt': idx,
                'weight_raw': rec.get('weight', '—'),
                'weight_mg': round(w_mg, 2) if w_mg is not None else None,
                'datetime': rec.get('datetime', '—'),
                'balance_type': rec.get('balance_type', '—'),
                'snr': rec.get('snr', '—'),
                'status': 'pending',
                'status_label': '—',
            })

        # ── Pharmacopoeia statistics ───────────────────────────────────────
        stats_formatted = {}   # default nếu không parse được khối lượng nào
        if weights_mg:
            n = len(weights_mg)
            mean_mg = sum(weights_mg) / n
            lower_5 = mean_mg * 0.95
            upper_5 = mean_mg * 1.05
            lower_10 = mean_mg * 0.90
            upper_10 = mean_mg * 1.10

            out_5 = 0
            out_10 = 0
            for r in parsed_records:
                w = r['weight_mg']
                if w is None:
                    r['status'] = 'missing'
                    r['status_label'] = '—'
                    continue
                if w < lower_10 or w > upper_10:
                    r['status'] = 'out10'
                    r['status_label'] = '> ±10%'
                    out_10 += 1
                    out_5 += 1   # also counts as outside ±5%
                elif w < lower_5 or w > upper_5:
                    r['status'] = 'out5'
                    r['status_label'] = '> ±5%'
                    out_5 += 1
                else:
                    r['status'] = 'ok'
                    r['status_label'] = 'Đạt'

            # Rule: ≤2 outside ±5%  AND  0 outside ±10%
            pass_fail = 'Đạt' if (out_5 <= 2 and out_10 == 0) else 'Không đạt'

            # Format stats with comma as decimal separator
            def fmt_comma(val):
                if val is None:
                    return '—'
                return f"{val:.2f}".replace('.', ',')

            stats_formatted = {
                'n': n,
                'mean_mg': fmt_comma(mean_mg),
                'min_mg': fmt_comma(min(weights_mg)),
                'max_mg': fmt_comma(max(weights_mg)),
                'lower_5':  fmt_comma(lower_5),
                'upper_5':  fmt_comma(upper_5),
                'lower_10': fmt_comma(lower_10),
                'upper_10': fmt_comma(upper_10),
                'out_5': out_5,
                'out_10': out_10,
                'pass_fail': pass_fail,
                'pass_fail_class': 'pass' if pass_fail == 'Đạt' else 'fail',
            }

        # ── Common metadata (first non-empty value wins) ──────────────────
        def first_valid(key):
            for r in records:
                v = str(r.get(key, '') or '').strip()
                if v and v != '-' and v != '—':
                    return v
            return '—'

        balance_type = first_valid('balance_type')
        snr = first_valid('snr')
        raw_date = first_valid('datetime')
        scan_date = raw_date.split(' ')[0] if ' ' in raw_date else raw_date

        # ── Save records to database ──────────────────────────────────────
        # 1. Tạo MedicineItem đại diện cho lô cân này
        # drug_info keys từ scan.html: name, generic, lot, std, analysis, report, stage, issue
        drug_name = (drug_info.get('name') or '').strip() or 'Phiếu cân Lab'
        batch_no  = (drug_info.get('lot') or '').strip() or snr or scan_date

        # Chuẩn hoá drug_info để template dynamic_coa.html dùng nhất quán
        drug_info_ctx = {
            'drug_name':       drug_name,
            'generic_name':    drug_info.get('generic', ''),
            'lot_number':      batch_no,
            'std_number':      drug_info.get('std', ''),
            'analysis_number': drug_info.get('analysis', ''),
            'report_number':   drug_info.get('report', ''),
            'stage':           drug_info.get('stage', 'BAO PHIM'),
            'issue':           drug_info.get('issue', '01'),
        }

        med = MedicineItem.objects.create(
            trade_name=drug_name,
            active_ingredient=drug_info_ctx['generic_name'],
            strength='',
            dosage_form='Viên nén',
            manufacturer='',
            batch_number=batch_no,
            registration_number=drug_info_ctx['std_number'],
            mfg_date='',
            exp_date='',
            indications=f"Phiếu kiểm nghiệm ĐĐKL - {drug_info_ctx['analysis_number']}",
        )

        # 2. Tạo ScannedDocument để gắn vào lịch sử dashboard
        file_label = f"[Phiếu cân] {drug_name} - Lô {batch_no}"
        doc_record = ScannedDocument.objects.create(
            user=request.user,
            medicine=med,
            file_name=file_label,
            accuracy_score=99.0,
            status='pending',
        )
        
        log_action(request, 'MEDICINE_CREATED', target_type='MedicineItem', target_label=med.trade_name)
        log_action(request, 'DOC_SCANNED', target_type='ScannedDocument', target_label=file_label, target_id=doc_record.id)

        # 3. Lưu các bản ghi cân và gắn vào ScannedDocument
        for r in parsed_records:
            WeightUniformityRecord.objects.create(
                user=request.user,
                scanned_document=doc_record,
                pill_number=r['stt'],
                weight=str(r['weight_raw']),
                timestamp=timezone.now(),
                balance_type=str(r['balance_type']),
                snr=str(r['snr']),
            )

        context = {
            'stats': stats_formatted if weights_mg else {},
            'balance_type': balance_type,
            'snr': snr,
            'scan_date': scan_date,
            'drug_info': drug_info_ctx,
            'user': request.user,
            'generated_at': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
            'doc_id': doc_record.id if doc_record else None,
        }

        context['parsed_records'] = parsed_records

        chunked_records = []
        for i in range(0, len(parsed_records), 20):
            chunk_list = parsed_records[i:i+20]
            chunk_dict = {}
            for j in range(1, 21):
                w_val = '—'
                if j - 1 < len(chunk_list):
                    r = chunk_list[j - 1]
                    if r['weight_mg'] is not None:
                        w_val = f"{r['weight_mg']:.2f}".replace('.', ',')
                chunk_dict[f'w{j}'] = w_val
            
            c_weights = [r['weight_mg'] for r in chunk_list if r['weight_mg'] is not None]
            c_stats = {}
            if c_weights:
                cn = len(c_weights)
                cmean = sum(c_weights) / cn
                cl5 = cmean * 0.95
                cu5 = cmean * 1.05
                cl10 = cmean * 0.90
                cu10 = cmean * 1.10
                
                cout5 = 0
                cout10 = 0
                for cw in c_weights:
                    if cw < cl10 or cw > cu10:
                        cout10 += 1
                        cout5 += 1
                    elif cw < cl5 or cw > cu5:
                        cout5 += 1
                
                cpass = 'Đạt' if (cout5 <= 2 and cout10 == 0) else 'Không đạt'
                def fmt_c(val): return f"{val:.2f}".replace('.', ',') if val is not None else '—'
                
                c_stats = {
                    'n': cn, 'mean_mg': fmt_c(cmean), 'min_mg': fmt_c(min(c_weights)),
                    'max_mg': fmt_c(max(c_weights)), 'lower_5': fmt_c(cl5), 'upper_5': fmt_c(cu5),
                    'lower_10': fmt_c(cl10), 'upper_10': fmt_c(cu10),
                    'out_5': cout5, 'out_10': cout10, 'pass_fail': cpass
                }
            chunk_dict['stats'] = c_stats if c_stats else stats_formatted
            chunked_records.append(chunk_dict)
            
        if not chunked_records:
            chunk_dict = {f'w{j}': '—' for j in range(1, 21)}
            chunk_dict['stats'] = stats_formatted
            chunked_records.append(chunk_dict)

        context['chunked_records'] = chunked_records

        from django.template.loader import render_to_string
        html_content = render_to_string('user/dynamic_coa.html', context)

        return JsonResponse({
            'success': True,
            'html': html_content,
            'statistics': stats_formatted,
            'doc_id': doc_record.id,
            'medicine_id': med.id,
        })


    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
    except Exception as e:
        logger.error(f"Error generating COA: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Lỗi hệ thống: {str(e)}'}, status=500)



@login_required(login_url='login')
def save_coa_report(request):
    if request.method == 'POST':
        html_content = request.POST.get('html_content')
        doc_id = request.POST.get('doc_id')
        
        if not html_content:
            return JsonResponse({'success': False, 'error': 'Không có dữ liệu HTML'})
            
        doc_record = None
        if doc_id:
            try:
                doc_record = ScannedDocument.objects.get(id=doc_id)
            except ScannedDocument.DoesNotExist:
                pass
                
        saved_report = SavedCOAReport.objects.create(
            user=request.user,
            scanned_document=doc_record,
            html_content=html_content
        )
        
        doc_name = doc_record.file_name if doc_record else "Phiếu COA Độc Lập"
        log_action(request, 'COA_SAVED', target_type='SavedCOAReport', target_label=doc_name, target_id=saved_report.id)
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Yêu cầu không hợp lệ'})

@login_required(login_url='login')
def view_saved_coa(request, report_id):
    try:
        report = SavedCOAReport.objects.get(id=report_id)
        from django.http import HttpResponse
        
        # Inject Javascript to hide the save button when viewing a saved report
        html = report.html_content
        hide_script = "<script>document.addEventListener('DOMContentLoaded', () => { var btn = document.getElementById('btn-save-coa'); if(btn) btn.style.display='none'; });</script>"
        if '</body>' in html:
            html = html.replace('</body>', hide_script + '</body>')
        else:
            html += hide_script
            
        full_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Phiếu Báo Cáo Đã Lưu</title>
<style>
@media print {{
  .no-print {{ display: none !important; }}
  body {{ background: #fff !important; margin: 0; }}
  .pf {{ margin: 0; padding: 0 !important; box-shadow: none !important; page-break-after: always; width: 100% !important; border: none !important; }}
}}
body {{ background: #e0e0e0; font-family: 'Times New Roman', Times, serif; font-size: 13pt; margin: 0; padding: 0; }}
#page-container {{ display: flex; flex-direction: column; align-items: center; gap: 20px; padding: 20px; }}
.pf {{ background: white; width: 210mm; min-height: 297mm; padding: 15mm; box-shadow: 0 4px 12px rgba(0,0,0,0.1); box-sizing: border-box; position: relative; margin: 0 auto; outline: 1px solid #ccc; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 10px; }}
table, th, td {{ border: 1px solid black; }}
th, td {{ padding: 4px; text-align: center; vertical-align: middle; }}
.no-border, .no-border th, .no-border td {{ border: none !important; text-align: left; }}
.header-table td {{ border: 1px solid black; }}
h1, h2, h3 {{ margin: 0; padding: 0; font-size: 13pt; }}
.section-title {{ font-weight: bold; margin-top: 10px; margin-bottom: 5px; text-align: left; }}
</style>
</head>
<body>
<div class="no-print" style="background: #1e40af; color: #fff; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; font-family: Arial, sans-serif; font-size: 13px; z-index: 9999; position: sticky; top: 0;">
  <div>
    <span style="font-size: 15px; font-weight: bold;">📄 Phiếu Báo Cáo Đã Lưu</span>
  </div>
  <div style="display: flex; gap: 10px;">
    <button onclick="window.print()" style="padding: 7px 18px; border: 1px solid rgba(255,255,255,0.4); border-radius: 4px; background: #16a34a; color: #fff; cursor: pointer; font-size: 13px; font-weight: bold;">🖨️ In phiếu</button>
    <button onclick="window.close()" style="padding: 7px 18px; border: 1px solid rgba(255,255,255,0.4); border-radius: 4px; background: rgba(255,255,255,0.15); color: #fff; cursor: pointer; font-size: 13px;">✕ Đóng</button>
  </div>
</div>
<div id="page-container">
{html}
</div>
</body>
</html>"""
        return HttpResponse(full_html)
    except SavedCOAReport.DoesNotExist:
        return HttpResponse('Không tìm thấy phiếu đã lưu', status=404)
