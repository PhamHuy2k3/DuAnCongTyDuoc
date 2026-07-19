import os
import django
import sys
from django.conf import settings

sys.path.append('c:/ITC_Subjects_HKV/DuAnThucTap/DuAnCongTyDuoc')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.template.loader import render_to_string

# mock chunked_records with 45 records
records = [{'weight_mg': i} for i in range(1, 46)]
chunked_records = []
for i in range(0, len(records), 20):
    chunk_list = records[i:i+20]
    chunk_dict = {}
    for j in range(1, 21):
        w_val = '—'
        if j - 1 < len(chunk_list):
            w_val = f"{chunk_list[j-1]['weight_mg']:.2f}"
        chunk_dict[f'w{j}'] = w_val
    chunk_dict['stats'] = {'mean_mg': '10', 'pass_fail': 'Đạt'}
    chunked_records.append(chunk_dict)

context = {
    'chunked_records': chunked_records,
    'snr': 'Test SNR',
    'generated_at': '123'
}

html = render_to_string('user/dynamic_coa.html', context)
with open('c:/ITC_Subjects_HKV/DuAnThucTap/DuAnCongTyDuoc/scratch/test_coa.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Generated test_coa.html")
