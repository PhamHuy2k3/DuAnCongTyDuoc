import codecs

with codecs.open('core/user/views.py', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace(
    'from .models import ScannedDocument, MedicineItem, WeightUniformityRecord',
    'from .models import ScannedDocument, MedicineItem, WeightUniformityRecord, SavedCOAReport'
)

content = content.replace(
    '''        avg_accuracy = 0
        if total_scans > 0:
            avg_accuracy = docs.filter(accuracy_score__gt=0).aggregate(Avg('accuracy_score'))['accuracy_score__avg'] or 0
            avg_accuracy = round(avg_accuracy, 1)

        context = {''',
    '''        avg_accuracy = 0
        if total_scans > 0:
            avg_accuracy = docs.filter(accuracy_score__gt=0).aggregate(Avg('accuracy_score'))['accuracy_score__avg'] or 0
            avg_accuracy = round(avg_accuracy, 1)

        saved_reports = SavedCOAReport.objects.filter(user=request.user).order_by('-saved_at')

        context = {
            'saved_reports': saved_reports,'''
)

content = content.replace(
    '''            'user': request.user,
            'generated_at': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
        }

        # Truyền tất cả records vào context''',
    '''            'user': request.user,
            'generated_at': timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
            'doc_id': doc_record.id if doc_record else None,
        }

        # Truyền tất cả records vào context'''
)

new_views = '''

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
                
        SavedCOAReport.objects.create(
            user=request.user,
            scanned_document=doc_record,
            html_content=html_content
        )
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
'''

with codecs.open('core/user/views.py', 'w', 'utf-8') as f:
    f.write(content + new_views)
