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
from .models import ScannedDocument, MedicineItem, WeightUniformityRecord
from .services import process_image, validate_image_file, extract_balance_receipt_records
import json
import os
import re
import logging
from datetime import datetime
from django.db.models import Avg

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
        stats = {}
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
        for r in parsed_records:
            WeightUniformityRecord.objects.create(
                user=request.user,
                pill_number=r['stt'],
                weight=str(r['weight_raw']),
                timestamp=timezone.now(),
                balance_type=str(r['balance_type']),
                snr=str(r['snr']),
            )

        context = {
            'stats': stats_formatted,
            'balance_type': balance_type,
            'snr': snr,
            'scan_date': scan_date,
            'drug_info': drug_info,
            'user': request.user,
            'generated_at': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
        }

        for i in range(1, 21):
            w_val = '—'
            if i - 1 < len(parsed_records):
                r = parsed_records[i - 1]
                if r['weight_mg'] is not None:
                    w_val = f"{r['weight_mg']:.2f}".replace('.', ',')
            context[f'w{i}'] = w_val

        from django.template.loader import render_to_string
        html_content = render_to_string('user/dynamic_coa.html', context)

        return JsonResponse({
            'success': True,
            'html': html_content,
            'statistics': stats,
        })


    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Dữ liệu JSON không hợp lệ'}, status=400)
    except Exception as e:
        logger.error(f"Error generating COA: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Lỗi hệ thống: {str(e)}'}, status=500)

