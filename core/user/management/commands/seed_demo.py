from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from user.models import MedicineItem, ScannedDocument
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo data for dashboard'

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(
            username='demo_user',
            defaults={
                'email': 'demo@pharmascan.com',
                'role': 'USER',
                'is_password_changed': True,
            }
        )
        if user.plain_password_temp != 'demo1234':
            user.set_password('demo1234')
            user.plain_password_temp = 'demo1234'
            user.save()

        med_data = [
            {
                'trade_name': 'Paracetamol Extra',
                'active_ingredient': 'Acetaminophen (Paracetamol)',
                'strength': '500mg',
                'dosage_form': 'Viên nén bao phim',
                'manufacturer': 'Công ty Cổ phần Dược phẩm Medipharco',
                'batch_number': 'LOT-PARA2026',
                'registration_number': 'VD-21588-14',
                'mfg_date': '20/05/2026',
                'exp_date': '20/05/2029',
                'indications': 'Giảm đau từ nhẹ đến trung bình, hạ sốt.',
            },
            {
                'trade_name': 'Amoxipharm 250',
                'active_ingredient': 'Amoxicillin Trihydrate',
                'strength': '250mg',
                'dosage_form': 'Viên nang cứng',
                'manufacturer': 'Tổng công ty Dược Việt Nam (Vinapharm)',
                'batch_number': 'LOT-AMOX9925',
                'registration_number': 'VD-18239-12',
                'mfg_date': '12/03/2026',
                'exp_date': '12/03/2029',
                'indications': 'Điều trị nhiễm khuẩn đường hô hấp, da, tiết niệu.',
            },
            {
                'trade_name': 'BioFlu-TC',
                'active_ingredient': 'Kháng nguyên Virus Cúm bất hoạt',
                'strength': '0.5ml / Liều',
                'dosage_form': 'Hỗn dịch tiêm',
                'manufacturer': 'Viện Vắc xin và Sinh phẩm Y tế IVAC',
                'batch_number': 'LOT-VAC4082',
                'registration_number': 'QLSP-1102-25',
                'mfg_date': '01/01/2026',
                'exp_date': '01/01/2028',
                'indications': 'Phòng ngừa bệnh cúm mùa.',
            },
            {
                'trade_name': 'Zandyrine 10 mg',
                'active_ingredient': 'Amlodipine besylate',
                'strength': '10mg',
                'dosage_form': 'Viên nén bao phim',
                'manufacturer': 'Công ty Dược phẩm Trung ương I',
                'batch_number': 'LOT-ZAN4086',
                'registration_number': 'VD-32456-19',
                'mfg_date': '01/04/2026',
                'exp_date': '31/03/2029',
                'indications': 'Điều trị tăng huyết áp, đau thắt ngực.',
            },
            {
                'trade_name': 'Cefixime 200mg',
                'active_ingredient': 'Cefixime trihydrate',
                'strength': '200mg',
                'dosage_form': 'Viên nang cứng',
                'manufacturer': 'Công ty Dược phẩm Đạt Vi Phú',
                'batch_number': 'LOT-CEFI2026',
                'registration_number': 'VD-28765-16',
                'mfg_date': '15/02/2026',
                'exp_date': '15/02/2028',
                'indications': 'Nhiễm khuẩn hô hấp, tai mũi họng, tiết niệu.',
            },
        ]

        file_names = [
            'PhieuThongTin_Paracetamol_500mg.docx',
            'ChungNhanChatLuong_Amoxicillin_250mg.docx',
            'XacNhanNhapKhau_BioFlu_Vaccine.docx',
            'ToaThuoc_Zandyrine_10mg.docx',
            'PhieuKiemNghiem_Cefixime_200mg.docx',
        ]

        statuses = ['pending', 'approved', 'approved', 'rejected', 'approved']

        created_count = 0
        for i, data in enumerate(med_data):
            med, _ = MedicineItem.objects.get_or_create(
                batch_number=data['batch_number'],
                defaults={
                    **data,
                    'approved_by': user if statuses[i] == 'approved' else None,
                    'approved_at': timezone.now() if statuses[i] == 'approved' else None,
                }
            )
            if statuses[i] == 'approved' and med.approved_by is None:
                med.approved_by = user
                med.approved_at = timezone.now()
                med.save()

            doc, created = ScannedDocument.objects.get_or_create(
                file_name=file_names[i],
                defaults={
                    'user': user,
                    'status': statuses[i],
                    'accuracy_score': round(random.uniform(95.0, 99.9), 1),
                    'medicine': med,
                    'scanned_at': timezone.now() - timedelta(days=i),
                    'reviewed_by': user if statuses[i] != 'pending' else None,
                    'reviewed_at': timezone.now() - timedelta(days=i) if statuses[i] != 'pending' else None,
                }
            )
            if created:
                created_count += 1

        for i in range(3):
            ScannedDocument.objects.get_or_create(
                file_name=f'DuLieuQuet_{i+1}.docx',
                defaults={
                    'user': user,
                    'status': 'approved',
                    'accuracy_score': round(random.uniform(96.0, 99.5), 1),
                    'scanned_at': timezone.now() - timedelta(days=10 + i),
                }
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} demo documents and medicines.'))
