from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('scan/', views.scan_demo, name='scan_demo'),
    path('scan/upload/', views.upload_document, name='upload_document'),
    path('scan/receipt-api/', views.scan_receipt_api, name='scan_receipt_api'),
    path('scan/multi-api/', views.scan_multi_api, name='scan_multi_api'),
    path('scan/coa-api/', views.generate_coa_from_scanned_data, name='generate_coa_api'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('coa/', views.coa_view, name='coa_report'),
    path('save-coa/', views.save_coa_report, name='save_coa_report'),
    path('view-saved-coa/<int:report_id>/', views.view_saved_coa, name='view_saved_coa'),

    # ── Dashboard ───────────────────────────────────────────────────────────
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),

    # ── ScannedDocument CRUD ─────────────────────────────────────────────────
    path('dashboard/documents/', views.document_list_api, name='document_list_api'),
    path('dashboard/documents/<int:doc_id>/', views.document_detail, name='document_detail'),
    path('dashboard/documents/<int:doc_id>/delete/', views.delete_document, name='delete_document'),
    path('dashboard/approve/<int:doc_id>/', views.approve_document, name='approve_document'),
    path('dashboard/reject/<int:doc_id>/', views.reject_document, name='reject_document'),

    # ── MedicineItem CRUD ────────────────────────────────────────────────────
    path('dashboard/medicines/', views.medicine_list_api, name='medicine_list_api'),
    path('dashboard/medicines/create/', views.medicine_create, name='medicine_create'),
    path('dashboard/medicines/<int:med_id>/update/', views.medicine_update, name='medicine_update'),
    path('dashboard/medicines/<int:med_id>/delete/', views.medicine_delete, name='medicine_delete'),
]
