import codecs

with codecs.open('core/user/views.py', 'r', 'utf-8') as f:
    content = f.read()

target = '''        # Truyền tất cả records vào context (không giới hạn 20)
        context['parsed_records'] = parsed_records

        # Vẫn giữ w1-w20 để tương thích ngược với phần cứng trong template
        for i in range(1, 21):
            w_val = '—'
            if i - 1 < len(parsed_records):
                r = parsed_records[i - 1]
                if r['weight_mg'] is not None:
                    w_val = f"{r['weight_mg']:.2f}".replace('.', ',')
            context[f'w{i}'] = w_val'''

replacement = '''        context['parsed_records'] = parsed_records
        context['doc_id'] = doc_record.id if doc_record else None

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

        context['chunked_records'] = chunked_records'''

content = content.replace(target, replacement)

with codecs.open('core/user/views.py', 'w', 'utf-8') as f:
    f.write(content)
