import codecs

with codecs.open('core/user/views.py', 'r', 'utf-8') as f:
    content = f.read()

# We need to find the start of drug_info_ctx block and the end of generate_coa_from_scanned_data
start_marker = "        # Chuẩn hoá drug_info để template dynamic_coa.html dùng nhất quán"
end_marker = "    except json.JSONDecodeError:"

if start_marker in content and end_marker in content:
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    new_block = '''        # Chuẩn hoá drug_info để template dynamic_coa.html dùng nhất quán
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
        for i in range(0, len(parsed_records), 1):
            chunk_list = parsed_records[i:i+1]
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


'''
    
    new_content = content[:start_idx] + new_block + content[end_idx:]
    with codecs.open('core/user/views.py', 'w', 'utf-8') as f:
        f.write(new_content)
    print("Fixed.")
else:
    print("Markers not found.")
