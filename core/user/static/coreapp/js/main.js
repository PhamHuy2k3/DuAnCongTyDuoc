document.addEventListener('DOMContentLoaded', () => {
    const header = document.getElementById('header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    const demoOpBtn = document.getElementById('btn-demo-operator');
    const demoAdminBtn = document.getElementById('btn-demo-admin');
    const loginEmailInput = document.getElementById('login-email');
    const loginPasswordInput = document.getElementById('login-password');
    const loginForm = document.getElementById('login-form');

    if (demoOpBtn && demoAdminBtn) {
        demoOpBtn.addEventListener('click', () => {
            if (loginEmailInput && loginPasswordInput) {
                loginEmailInput.value = demoOpBtn.getAttribute('data-email');
                loginPasswordInput.value = 'operator123';
                addAuthGlowEffect();
                setTimeout(() => {
                    window.location.href = demoOpBtn.getAttribute('data-redirect');
                }, 900);
            }
        });

        demoAdminBtn.addEventListener('click', () => {
            if (loginEmailInput && loginPasswordInput) {
                loginEmailInput.value = demoAdminBtn.getAttribute('data-email');
                loginPasswordInput.value = 'admin123';
                addAuthGlowEffect();
                setTimeout(() => {
                    window.location.href = demoAdminBtn.getAttribute('data-redirect');
                }, 900);
            }
        });

        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                addAuthGlowEffect();
                const email = loginEmailInput.value;
                setTimeout(() => {
                    if (email.includes('admin')) {
                        window.location.href = '/dashboard/';
                    } else {
                        window.location.href = 'user/scan/';
                    }
                }, 800);
            });
        }
    }

    function addAuthGlowEffect() {
        const card = document.querySelector('.auth-card');
        if (card) {
            card.style.borderColor = 'var(--primary)';
            card.style.boxShadow = '0 0 25px var(--primary-glow)';
        }
    }

    const sidebarMenuItems = document.querySelectorAll('.db-menu-item');
    const tabPanes = document.querySelectorAll('.db-tab-pane');
    const dbTabTitle = document.getElementById('db-tab-title');

    if (sidebarMenuItems.length > 0) {
        sidebarMenuItems.forEach(item => {
            item.addEventListener('click', () => {
                const targetTabId = item.getAttribute('data-tab');
                
                sidebarMenuItems.forEach(menu => menu.classList.remove('active'));
                item.classList.add('active');

                tabPanes.forEach(pane => {
                    pane.classList.add('hidden');
                    pane.classList.remove('active');
                });
                const targetPane = document.getElementById(targetTabId);
                if (targetPane) {
                    targetPane.classList.remove('hidden');
                    targetPane.classList.add('active');
                }

                if (dbTabTitle) {
                    dbTabTitle.textContent = item.querySelector('span').textContent;
                }
            });
        });

        const liveDateEl = document.getElementById('db-live-date');
        if (liveDateEl) {
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            const today = new Date();
            liveDateEl.textContent = today.toLocaleDateString('vi-VN', options);
        }

        const btnTriggerAudit = document.getElementById('btn-trigger-audit');
        const rowPendingAmox = document.getElementById('row-pending-amox');
        const auditModal = document.getElementById('audit-modal');
        const btnCloseAuditModal = document.getElementById('btn-close-audit-modal');
        const btnAuditApprove = document.getElementById('btn-audit-approve');
        const btnAuditReject = document.getElementById('btn-audit-reject');

        if (rowPendingAmox && auditModal) {
            const openModal = () => {
                auditModal.classList.remove('hidden');
            };
            
            rowPendingAmox.addEventListener('click', openModal);
            
            if (btnTriggerAudit) {
                btnTriggerAudit.addEventListener('click', (e) => {
                    e.stopPropagation();
                    openModal();
                });
            }

            btnCloseAuditModal.addEventListener('click', () => {
                auditModal.classList.add('hidden');
            });

            auditModal.addEventListener('click', (e) => {
                if (e.target === auditModal) {
                    auditModal.classList.add('hidden');
                }
            });

            btnAuditApprove.addEventListener('click', () => {
                btnAuditApprove.textContent = 'Đang lưu vào kho...';
                btnAuditApprove.setAttribute('disabled', 'true');
                btnAuditReject.setAttribute('disabled', 'true');
                
                setTimeout(() => {
                    const badge = document.getElementById('badge-pending-amox');
                    if (badge) {
                        badge.textContent = 'Đã Duyệt';
                        badge.className = 'status-pill green-pill';
                    }
                    if (rowPendingAmox) {
                        rowPendingAmox.style.cursor = 'default';
                        rowPendingAmox.classList.remove('table-row-pending');
                        rowPendingAmox.removeEventListener('click', openModal);
                    }
                    if (btnTriggerAudit) {
                        btnTriggerAudit.textContent = 'Đã lưu';
                        btnTriggerAudit.setAttribute('disabled', 'true');
                        btnTriggerAudit.className = 'btn btn-secondary btn-nav';
                    }

                    const kpiPending = document.getElementById('kpi-pending');
                    const kpiApproved = document.getElementById('kpi-approved');
                    const sideBubble = document.getElementById('side-pending-bubble');

                    if (kpiPending) kpiPending.textContent = '0';
                    if (kpiApproved) kpiApproved.textContent = '48';
                    if (sideBubble) sideBubble.style.display = 'none';

                    const dynamicRow = document.getElementById('dynamic-row-amox');
                    if (dynamicRow) {
                        dynamicRow.classList.remove('hidden');
                        
                        document.getElementById('dyn-trade').textContent = document.getElementById('aud-trade_name').value;
                        document.getElementById('dyn-active').textContent = document.getElementById('aud-active_ingredient').value;
                        document.getElementById('dyn-strength').textContent = document.getElementById('aud-strength').value;
                        document.getElementById('dyn-dosage').textContent = document.getElementById('aud-dosage_form').value;
                        document.getElementById('dyn-reg').textContent = document.getElementById('aud-registration_number').value;
                        document.getElementById('dyn-batch').textContent = document.getElementById('aud-batch_number').value;
                        document.getElementById('dyn-exp').textContent = document.getElementById('aud-exp_date').value;
                    }

                    auditModal.classList.add('hidden');
                    alert('Phê duyệt dược phẩm thành công! Thông tin thuốc đã được chuẩn hóa và đồng bộ vào kho dược số hóa.');
                    
                    btnAuditApprove.textContent = 'Duyệt & Lưu Vào Kho Thuốc';
                    btnAuditApprove.removeAttribute('disabled');
                    btnAuditReject.removeAttribute('disabled');
                }, 1200);
            });

            btnAuditReject.addEventListener('click', () => {
                const badge = document.getElementById('badge-pending-amox');
                if (badge) {
                    badge.textContent = 'Bị Từ Chối';
                    badge.className = 'status-pill red-pill';
                }
                if (rowPendingAmox) {
                    rowPendingAmox.style.cursor = 'default';
                    rowPendingAmox.classList.remove('table-row-pending');
                    rowPendingAmox.removeEventListener('click', openModal);
                }
                if (btnTriggerAudit) {
                    btnTriggerAudit.textContent = 'Lỗi dữ liệu';
                    btnTriggerAudit.setAttribute('disabled', 'true');
                    btnTriggerAudit.className = 'btn btn-secondary btn-nav';
                }

                const kpiPending = document.getElementById('kpi-pending');
                const sideBubble = document.getElementById('side-pending-bubble');
                if (kpiPending) kpiPending.textContent = '0';
                if (sideBubble) sideBubble.style.display = 'none';
                
                auditModal.classList.add('hidden');
            });
        }

        const btnExportExcel = document.getElementById('btn-export-excel');
        const dlProgressBox = document.getElementById('dl-progress-box');
        const dlProgressFill = document.getElementById('dl-progress-fill');
        const dlStatusLabel = document.getElementById('dl-status-label');

        if (btnExportExcel) {
            btnExportExcel.addEventListener('click', () => {
                btnExportExcel.setAttribute('disabled', 'true');
                dlProgressBox.classList.remove('hidden');
                
                let progress = 0;
                dlProgressFill.style.width = '0%';
                
                const interval = setInterval(() => {
                    progress += 5;
                    dlProgressFill.style.width = `${progress}%`;

                    if (progress <= 30) {
                        dlStatusLabel.textContent = 'Đang nén dữ liệu kho...';
                    } else if (progress <= 65) {
                        dlStatusLabel.textContent = 'Đang lập bảng biểu Excel...';
                    } else if (progress < 100) {
                        dlStatusLabel.textContent = 'Đang xuất tệp XLSX...';
                    } else {
                        clearInterval(interval);
                        dlStatusLabel.textContent = 'Xuất file thành công! 📥';
                        
                        setTimeout(() => {
                            dlProgressBox.classList.add('hidden');
                            btnExportExcel.removeAttribute('disabled');
                        }, 1800);
                    }
                }, 80);
            });
        }
    }

    const dropzone = document.getElementById('document-dropzone');
    if (!dropzone) return;

    const fileInput = document.getElementById('file-input');
    const dropzonePrompt = document.getElementById('dropzone-prompt');
    const fileLoadedView = document.getElementById('file-loaded-view');
    const loadedFileName = document.getElementById('loaded-file-name');
    const btnResetScan = document.getElementById('btn-reset-scan');
    const btnStartProcess = document.getElementById('btn-start-process');
    const laserLine = document.getElementById('laser-line');
    const consoleLogs = document.getElementById('console-logs');
    const formStatusBadge = document.getElementById('form-status-badge');
    const successModal = document.getElementById('success-modal');
    const btnModalClose = document.getElementById('btn-modal-close');
    const btnFormClear = document.getElementById('btn-form-clear');
    const btnFormSubmit = document.getElementById('btn-form-submit');
    const consoleStatusDot = document.querySelector('.console-status-dot');

    const tempPara = document.getElementById('temp-para');
    const tempAmox = document.getElementById('temp-amox');
    const tempVac = document.getElementById('temp-vac');
    const templateButtons = document.querySelectorAll('.btn-template');

    const btnTabWord = document.getElementById('btn-tab-word');
    const btnTabPhoto = document.getElementById('btn-tab-photo');
    const wordTemplatesBlock = document.getElementById('word-templates-selection');
    const photoTemplatesBlock = document.getElementById('photo-templates-selection');
    const filePhotoLoadedView = document.getElementById('file-photo-loaded-view');
    const btnResetPhoto = document.getElementById('btn-reset-photo');
    const panelWordForm = document.getElementById('panel-word-form');
    const panelPhotoForm = document.getElementById('panel-photo-form');
    
    const photoStatusBadge = document.getElementById('photo-status-badge');
    const valMean = document.getElementById('val-mean');
    const valRsd = document.getElementById('val-rsd');
    const valResult = document.getElementById('val-result');
    const btnPhotoClear = document.getElementById('btn-photo-clear');
    const btnSyncCoa = document.getElementById('btn-sync-coa');
    const photoLaserLine = document.getElementById('photo-laser-line');
    
    const ocrProgressBox = document.getElementById('ocr-progress-box');
    const ocrProgressFill = document.getElementById('ocr-progress-fill');
    const ocrProgressPercent = document.getElementById('ocr-progress-percent');
    const ocrProgressLabel = document.getElementById('ocr-progress-label');

    let currentScanMode = 'word';
    let selectedDocumentKey = null;
    let isProcessing = false;

    function setScanButtonState(enabled) {
        if (!btnStartProcess) return;
        if (enabled) {
            btnStartProcess.removeAttribute('disabled');
            btnStartProcess.classList.add('btn-glow-pulse');
        } else {
            btnStartProcess.setAttribute('disabled', 'true');
            btnStartProcess.classList.remove('btn-glow-pulse');
        }
    }

    const mockPillWeights = [
        "0.258", "0.255", "0.256", "0.254", "0.252", 
        "0.256", "0.260", "0.258", "0.255", "0.257",
        "0.259", "0.253", "0.258", "0.256", "0.255", 
        "0.255", "0.253", "0.258", "0.256", "0.255"
    ];

    function addLog(text, type = 'system') {
        if (!consoleLogs) return;
        const timestamp = new Date().toLocaleTimeString();
        const logLine = document.createElement('div');
        logLine.className = `log-line log-${type}`;
        logLine.innerHTML = `<span class="log-time" style="color: #64748b; margin-right: 8px;">[${timestamp}]</span> ${text}`;
        consoleLogs.appendChild(logLine);
        consoleLogs.scrollTop = consoleLogs.scrollHeight;
    }

    if (btnTabWord && btnTabPhoto) {
        btnTabWord.addEventListener('click', () => {
            if (isProcessing) return;
            currentScanMode = 'word';
            btnTabWord.classList.add('active');
            btnTabPhoto.classList.remove('active');
            
            wordTemplatesBlock.classList.remove('hidden');
            photoTemplatesBlock.classList.add('hidden');
            
            panelWordForm.classList.remove('hidden');
            panelPhotoForm.classList.add('hidden');
            
            filePhotoLoadedView.classList.add('hidden');
            if (selectedDocumentKey && selectedDocumentKey !== 'photo-lab') {
                fileLoadedView.classList.remove('hidden');
                setScanButtonState(true);
            } else {
                dropzonePrompt.classList.remove('hidden');
                setScanButtonState(false);
                updateDropzoneText('word');
            }
            
            document.getElementById('btn-start-text').textContent = 'Bắt đầu Quét & Tự động điền';
            addLog('Switched scan engine to: Word document template scanner.', 'system');
        });

        btnTabPhoto.addEventListener('click', () => {
            if (isProcessing) return;
            currentScanMode = 'photo';
            btnTabPhoto.classList.add('active');
            btnTabWord.classList.remove('active');
            
            photoTemplatesBlock.classList.remove('hidden');
            wordTemplatesBlock.classList.add('hidden');
            
            panelPhotoForm.classList.remove('hidden');
            panelWordForm.classList.add('hidden');
            
            fileLoadedView.classList.add('hidden');
            if (selectedDocumentKey === 'photo-lab') {
                dropzonePrompt.classList.add('hidden');
                filePhotoLoadedView.classList.remove('hidden');
                setScanButtonState(true);
            } else {
                filePhotoLoadedView.classList.add('hidden');
                dropzonePrompt.classList.remove('hidden');
                setScanButtonState(false);
                updateDropzoneText('photo');
            }
            
            document.getElementById('btn-start-text').textContent = 'Bắt đầu Quét AI OCR Phiếu Lab';
            
            addLog('Switched scan engine to: Lab balance receipt photo scanner.', 'system');
            resetPhotoFormInputs();
        });
    }

    const mockDocuments = {
        paracetamol: {
            fileName: 'PhieuThongTin_Paracetamol_500mg.docx',
            paperTitle: 'PHIẾU THÔNG TIN THUỐC',
            paperSub: 'Tên thương mại: Paracetamol Extra',
            paperP1: 'Hoạt chất chính: Acetaminophen (Paracetamol) hàm lượng 500mg. Tá dược vừa đủ một viên nén bao phim.',
            paperP2: 'Nhà sản xuất: Công ty Cổ phần Dược phẩm Medipharco. Địa chỉ: Cụm Công nghiệp Cầu Giấy, Hà Nội.',
            paperP3: 'Số đăng ký lưu hành: VD-21588-14. Số lô sản xuất: LOT-PARA2026. Ngày sản xuất: 20/05/2026. Hạn sử dụng: 3 năm kể từ ngày sản xuất (HSD: 20/05/2029).',
            paperP4: 'Chỉ định: Giảm đau từ nhẹ đến trung bình bao gồm đau đầu, đau răng, đau cơ, sốt do cảm cúm hoặc nhiễm khuẩn đường hô hấp.',
            formData: {
                trade_name: 'Paracetamol Extra',
                active_ingredient: 'Acetaminophen (Paracetamol)',
                strength: '500mg',
                dosage_form: 'Viên nén bao phim',
                manufacturer: 'Công ty Cổ phần Dược phẩm Medipharco',
                batch_number: 'LOT-PARA2026',
                registration_number: 'VD-21588-14',
                mfg_date: '20/05/2026',
                exp_date: '20/05/2029',
                indications: 'Giảm đau từ nhẹ đến trung bình bao gồm đau đầu, đau răng, đau cơ, sốt do cảm cúm hoặc nhiễm khuẩn.'
            }
        },
        amoxicillin: {
            fileName: 'ChungNhanChatLuong_Amoxicillin_250mg.docx',
            paperTitle: 'PHIẾU KIỂM NGHIỆM CHẤT LƯỢNG',
            paperSub: 'Tên thương mại: Amoxipharm 250',
            paperP1: 'Hoạt chất chính: Amoxicillin Trihydrate tương đương Amoxicillin khan 250mg. Tá dược: Tinh bột ngô, Magnesi stearat vừa đủ 1 viên nang.',
            paperP2: 'Nhà sản xuất: Tổng công ty Dược Việt Nam (Vinapharm). Địa chỉ: Khu công nghiệp VSIP, Bình Dương.',
            paperP3: 'Số đăng ký lưu hành: VD-18239-12. Số lô sản xuất: LOT-AMOX9925. Ngày sản xuất: 12/03/2026. Hạn sử dụng: 36 tháng kể từ ngày sản xuất (HSD: 12/03/2029).',
            paperP4: 'Chỉ định: Các nhiễm khuẩn do vi khuẩn nhạy cảm gây ra ở đường hô hấp trên, đường hô hấp dưới, da và mô mềm, đường tiết niệu không biến chứng.',
            formData: {
                trade_name: 'Amoxipharm 250',
                active_ingredient: 'Amoxicillin Trihydrate',
                strength: '250mg',
                dosage_form: 'Viên nang cứng',
                manufacturer: 'Tổng công ty Dược Việt Nam (Vinapharm)',
                batch_number: 'LOT-AMOX9925',
                registration_number: 'VD-18239-12',
                mfg_date: '12/03/2026',
                exp_date: '12/03/2029',
                indications: 'Điều trị các nhiễm khuẩn ở đường hô hấp trên và dưới, da và mô mềm, đường tiết niệu do vi khuẩn nhạy cảm.'
            }
        },
        vaccine: {
            fileName: 'XacNhanNhapKhau_BioFlu_Vaccine.docx',
            paperTitle: 'CHỨNG NHẬN VẮC XIN NHẬP KHẨU',
            paperSub: 'Tên thương mại: BioFlu-TC',
            paperP1: 'Hoạt chất: Kháng nguyên Virus cúm phân mảnh, bất hoạt gồm 3 chủng tương đương hàm lượng 0.5ml mỗi liều tiêm đơn.',
            paperP2: 'Nhà sản xuất: Viện Vắc xin và Sinh phẩm Y tế IVAC. Địa chỉ: Đường Trần Phú, Nha Trang, Khánh Hòa.',
            paperP3: 'Số đăng ký lưu hành: QLSP-1102-25. Số lô sản xuất: LOT-VAC4082. Ngày sản xuất: 01/01/2026. Hạn sử dụng: 24 tháng (HSD: 01/01/2028).',
            paperP4: 'Chỉ định: Tạo miễn dịch chủ động phòng ngừa bệnh cúm gây ra bởi các virus cúm phân phụ nhóm A và các chủng nhóm B cho người lớn và trẻ em từ 6 tháng tuổi.',
            formData: {
                trade_name: 'BioFlu-TC',
                active_ingredient: 'Kháng nguyên Virus Cúm bất hoạt',
                strength: '0.5ml / Liều',
                dosage_form: 'Hỗn dịch tiêm',
                manufacturer: 'Viện Vắc xin và Sinh phẩm Y tế IVAC',
                batch_number: 'LOT-VAC4082',
                registration_number: 'QLSP-1102-25',
                mfg_date: '01/01/2026',
                exp_date: '01/01/2028',
                indications: 'Tạo miễn dịch chủ động phòng bệnh cúm mùa cho người lớn và trẻ em từ 6 tháng tuổi trở lên.'
            }
        }
    };

    function loadDocumentState(key) {
        if (isProcessing) return;
        selectedDocumentKey = key;
        
        templateButtons.forEach(btn => btn.classList.remove('active'));
        const activeBtn = document.querySelector(`[data-target="${key}"]`);
        if (activeBtn) activeBtn.classList.add('active');

        if (key === 'photo-lab') {
            dropzonePrompt.classList.add('hidden');
            fileLoadedView.classList.add('hidden');
            filePhotoLoadedView.classList.remove('hidden');
            setScanButtonState(true);

            addLog(`Loaded mock lab receipt: <strong>Phieu_Can_DDKL-03.png</strong>`, 'system');
            addLog(`Image processed. Signature and weights located. Ready to scan.`, 'system');
            resetPhotoFormInputs();
            return;
        }

        const doc = mockDocuments[key];
        if (!doc) return;
        
        loadedFileName.textContent = doc.fileName;
        document.getElementById('sim-content-title').textContent = doc.paperTitle;
        document.getElementById('sim-content-subtitle').textContent = doc.paperSub;
        document.getElementById('sim-content-p1').textContent = doc.paperP1;
        document.getElementById('sim-content-p2').textContent = doc.paperP2;
        document.getElementById('sim-content-p3').textContent = doc.paperP3;
        document.getElementById('sim-content-p4').textContent = doc.paperP4;

        dropzonePrompt.classList.add('hidden');
        fileLoadedView.classList.remove('hidden');
        filePhotoLoadedView.classList.add('hidden');
        setScanButtonState(true);

        addLog(`Loaded mock document: <strong>${doc.fileName}</strong>`, 'system');
        addLog(`Structure parsed to Word HTML Document. Ready to analyze.`, 'system');

        resetFormInputs();
    }

    templateButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetKey = button.getAttribute('data-target');
            loadDocumentState(targetKey);
        });
    });

    dropzonePrompt.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            simulateCustomFileUpload(file.name);
        }
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        if (!isProcessing) dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (isProcessing) return;

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            simulateCustomFileUpload(files[0].name);
        }
    });

    btnResetScan.addEventListener('click', (e) => {
        e.stopPropagation();
        if (isProcessing) return;
        resetToInitialState();
    });

    btnResetPhoto.addEventListener('click', (e) => {
        e.stopPropagation();
        if (isProcessing) return;
        
        selectedDocumentKey = null;
        filePhotoLoadedView.classList.add('hidden');
        dropzonePrompt.classList.remove('hidden');
        setScanButtonState(false);
        
        const photoBtn = document.getElementById('temp-photo-lab');
        if (photoBtn) photoBtn.classList.remove('active');
        
        addLog('Photo unloaded. System idle.', 'system');
        resetPhotoFormInputs();
    });

    function resetToInitialState() {
        selectedDocumentKey = null;
        fileInput.value = '';
        dropzonePrompt.classList.remove('hidden');
        fileLoadedView.classList.add('hidden');
        setScanButtonState(false);
        templateButtons.forEach(btn => btn.classList.remove('active'));
        
        addLog('Document unloaded. System idle.', 'system');
        resetFormInputs();
    }

    function resetFormInputs() {
        const formInputs = document.querySelectorAll('.form-input');
        const indicators = document.querySelectorAll('.extraction-indicator');
        
        formInputs.forEach(input => {
            if (input.id.startsWith('aud-') || input.classList.contains('pill-input')) return;
            input.value = '';
            input.placeholder = 'Chưa có dữ liệu';
            input.classList.remove('filled-highlight');
        });

        indicators.forEach(ind => {
            if (ind.id.startsWith('ind-w')) return;
            ind.className = 'extraction-indicator';
        });

        if (formStatusBadge) {
            formStatusBadge.textContent = 'Đang chờ quét...';
            formStatusBadge.className = 'status-badge';
        }
        if (btnFormClear) btnFormClear.setAttribute('disabled', 'true');
        if (btnFormSubmit) btnFormSubmit.setAttribute('disabled', 'true');
    }

    function resetPhotoFormInputs() {
        const pillInputs = document.querySelectorAll('.pill-input');
        const indicators = document.querySelectorAll('[id^="ind-w"]');
        const ocrBoxes = document.querySelectorAll('.ocr-box');

        pillInputs.forEach(input => {
            input.value = '';
            input.classList.remove('filled-highlight');
        });

        indicators.forEach(ind => {
            ind.className = 'extraction-indicator';
        });

        ocrBoxes.forEach(box => {
            box.className = 'ocr-box';
        });

        if (photoStatusBadge) {
            photoStatusBadge.textContent = 'Đang chờ quét...';
            photoStatusBadge.className = 'status-badge';
        }
        if (valMean) valMean.textContent = '--';
        if (valRsd) valRsd.textContent = '--';
        if (valResult) {
            valResult.textContent = 'Chờ dữ liệu';
            valResult.style.color = 'var(--text-muted)';
        }
        if (btnPhotoClear) btnPhotoClear.setAttribute('disabled', 'true');
        if (btnSyncCoa) btnSyncCoa.setAttribute('disabled', 'true');
    }

    function simulateCustomFileUpload(fileName) {
        if (isProcessing) return;
        
        const nameLower = fileName.toLowerCase();
        if (nameLower.endsWith('.jpg') || nameLower.endsWith('.jpeg') || nameLower.endsWith('.png')) {
            btnTabPhoto.click();
            addLog(`Analyzing uploaded photo: <strong>${fileName}</strong>`, 'system');
            
            setTimeout(() => {
                selectedDocumentKey = 'photo-lab';
                dropzonePrompt.classList.add('hidden');
                fileLoadedView.classList.add('hidden');
                filePhotoLoadedView.classList.remove('hidden');
                setScanButtonState(true);
                
                const photoBtn = document.getElementById('temp-photo-lab');
                if (photoBtn) photoBtn.classList.add('active');
                
                addLog(`Photo processed. Valid laboratory balance receipt signature match.`, 'success');
                
                if (btnStartProcess) {
                    btnStartProcess.click();
                }
            }, 800);
            return;
        }

        btnTabWord.click();
        addLog(`Analyzing uploaded file: <strong>${fileName}</strong>`, 'system');
        addLog(`Converting .docx binary stream into HTML components...`, 'process');
        
        setTimeout(() => {
            let mockKey = 'paracetamol';
            if (nameLower.includes('amox')) {
                mockKey = 'amoxicillin';
            } else if (nameLower.includes('vac') || nameLower.includes('flu')) {
                mockKey = 'vaccine';
            }

            loadDocumentState(mockKey);
            loadedFileName.textContent = fileName;
            addLog(`Successfully converted <strong>${fileName}</strong> to local HTML layout.`, 'success');
        }, 1200);
    }

    function typeValue(inputEl, indicatorEl, val, callback) {
        if (!inputEl) {
            if (callback) callback();
            return;
        }
        
        if (indicatorEl) indicatorEl.className = 'extraction-indicator extracting';
        inputEl.value = '';
        inputEl.placeholder = 'Đang trích xuất...';
        
        let idx = 0;
        const interval = setInterval(() => {
            if (idx < val.length) {
                inputEl.value += val.charAt(idx);
                idx++;
            } else {
                clearInterval(interval);
                inputEl.classList.add('filled-highlight');
                if (indicatorEl) indicatorEl.className = 'extraction-indicator success';
                if (callback) callback();
            }
        }, 15);
    }

    function updateDropzoneText(mode) {
        const titleEl = document.getElementById('dropzone-title-main');
        const supportEl = document.getElementById('dropzone-support-main');
        if (!titleEl || !supportEl) return;
        
        if (mode === 'word') {
            titleEl.textContent = 'Kéo & Thả file Word ở đây';
            supportEl.textContent = 'Hỗ trợ các định dạng: .docx, .doc, .pdf';
        } else {
            titleEl.textContent = 'Kéo & Thả ảnh Phiếu Cân ở đây';
            supportEl.textContent = 'Hỗ trợ các định dạng: .jpg, .jpeg, .png';
        }
    }

    btnStartProcess.addEventListener('click', () => {
        if (isProcessing) return;
        
        isProcessing = true;
        setScanButtonState(false);
        btnTabWord.setAttribute('disabled', 'true');
        btnTabPhoto.setAttribute('disabled', 'true');
        fileInput.setAttribute('disabled', 'true');
        
        if (currentScanMode === 'word') {
            if (!selectedDocumentKey) {
                isProcessing = false;
                setScanButtonState(true);
                btnTabWord.removeAttribute('disabled');
                btnTabPhoto.removeAttribute('disabled');
                fileInput.removeAttribute('disabled');
                return;
            }
            
            btnResetScan.setAttribute('disabled', 'true');
            templateButtons.forEach(btn => btn.setAttribute('disabled', 'true'));
            resetFormInputs();
            
            laserLine.classList.remove('hidden');
            formStatusBadge.textContent = 'Đang quét...';
            formStatusBadge.className = 'status-badge scanning';
            consoleStatusDot.className = 'console-status-dot active';
            
            if (ocrProgressBox) {
                ocrProgressBox.classList.remove('hidden');
                ocrProgressFill.style.width = '0%';
                ocrProgressPercent.textContent = '0%';
                ocrProgressLabel.textContent = 'Khởi động bộ trích xuất Word...';
            }
            
            const doc = mockDocuments[selectedDocumentKey];
            const dataKeys = Object.keys(doc.formData);
            const loggedMilestones = new Set();
            
            const duration = 2500;
            const startTime = performance.now();
            
            function updateWordScan(currentTime) {
                const elapsedTime = currentTime - startTime;
                const progress = Math.min(elapsedTime / duration, 1);
                const percent = Math.floor(progress * 100);
                
                if (ocrProgressFill) ocrProgressFill.style.width = `${percent}%`;
                if (ocrProgressPercent) ocrProgressPercent.textContent = `${percent}%`;
                
                if (percent >= 0) {
                    if (!loggedMilestones.has('w0')) {
                        loggedMilestones.add('w0');
                        addLog(`⚡ Bắt đầu trích xuất File Word tài liệu...`, 'process');
                    }
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Khởi động bộ phân tích Word...';
                }
                
                if (percent >= 12) {
                    if (!loggedMilestones.has('w12')) {
                        loggedMilestones.add('w12');
                        addLog(`Đang chuyển đổi cấu trúc XML thành các thành phần HTML...`, 'process');
                    }
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang chuyển đổi định dạng Word...';
                }
                
                if (percent >= 28) {
                    if (!loggedMilestones.has('w28')) {
                        loggedMilestones.add('w28');
                        addLog(`Áp dụng Mô hình Nhận diện Thực thể Dược học (NER)...`, 'process');
                    }
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang nhận diện thực thể thuốc...';
                }
                
                if (percent >= 45) {
                    if (!loggedMilestones.has('w45')) {
                        loggedMilestones.add('w45');
                        addLog(`Bản đồ hóa dữ liệu trích xuất vào các trường thông tin...`, 'process');
                        addLog(`Trích xuất thành công 10 khóa dữ liệu tiêu chuẩn.`, 'success');
                    }
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang ánh xạ các trường biểu mẫu...';
                }
                
                if (percent >= 50 && percent < 90) {
                    const fieldsToFill = Math.min(10, Math.floor((percent - 50) / 4));
                    if (ocrProgressLabel) ocrProgressLabel.textContent = `Đang điền thông tin thuốc (${fieldsToFill}/10)...`;
                    
                    for (let i = 0; i < fieldsToFill; i++) {
                        const key = dataKeys[i];
                        const val = doc.formData[key];
                        const inputEl = document.getElementById(key);
                        const indicatorEl = document.getElementById(`ind-${key}`);
                        
                        if (inputEl && inputEl.value === '') {
                            inputEl.value = val;
                            inputEl.classList.add('filled-highlight');
                            if (indicatorEl) indicatorEl.className = 'extraction-indicator success';
                            
                            const labelName = document.querySelector(`label[for="${key}"]`).textContent.replace('*', '').trim();
                            addLog(`Đã trích xuất trường <strong>${labelName}</strong>: "${val}"`, 'process');
                        }
                    }
                }
                
                if (percent >= 90) {
                    if (!loggedMilestones.has('w90')) {
                        loggedMilestones.add('w90');
                        addLog(`Bản đồ hóa dữ liệu hoàn tất. Đang kiểm tra tính toàn vẹn...`, 'success');
                    }
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang xác thực thông tin...';
                }
                
                if (percent < 100) {
                    requestAnimationFrame(updateWordScan);
                } else {
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Hoàn tất trích xuất tài liệu!';
                    
                    for (let i = 0; i < 10; i++) {
                        const key = dataKeys[i];
                        const val = doc.formData[key];
                        const inputEl = document.getElementById(key);
                        const indicatorEl = document.getElementById(`ind-${key}`);
                        if (inputEl && inputEl.value === '') {
                            inputEl.value = val;
                            inputEl.classList.add('filled-highlight');
                            if (indicatorEl) indicatorEl.className = 'extraction-indicator success';
                        }
                    }
                    
                    setTimeout(() => {
                        if (ocrProgressBox) ocrProgressBox.classList.add('hidden');
                        finishScanningProcess();
                        btnTabWord.removeAttribute('disabled');
                        btnTabPhoto.removeAttribute('disabled');
                        fileInput.removeAttribute('disabled');
                    }, 500);
                }
            }
            
            requestAnimationFrame(updateWordScan);
        } 
        else {
            btnResetPhoto.setAttribute('disabled', 'true');
            resetPhotoFormInputs();
            
            photoLaserLine.classList.remove('hidden');
            photoStatusBadge.textContent = 'Đang quét...';
            photoStatusBadge.className = 'status-badge scanning';
            consoleStatusDot.className = 'console-status-dot active';
            
            if (ocrProgressBox) {
                ocrProgressBox.classList.remove('hidden');
                ocrProgressFill.style.width = '0%';
                ocrProgressPercent.textContent = '0%';
                ocrProgressLabel.textContent = 'Khởi động máy quét AI OCR...';
            }
            
            const loggedMilestones = new Set();
            const duration = 2500;
            const startTime = performance.now();
            
            function updatePhotoScan(currentTime) {
                const elapsedTime = currentTime - startTime;
                const progress = Math.min(elapsedTime / duration, 1);
                const percent = Math.floor(progress * 100);
                
                if (ocrProgressFill) ocrProgressFill.style.width = `${percent}%`;
                if (ocrProgressPercent) ocrProgressPercent.textContent = `${percent}%`;
                
                if (percent >= 0) {
                    if (!loggedMilestones.has('p0')) {
                        loggedMilestones.add('p0');
                        addLog(`⚡ Bắt đầu Quét AI OCR Phiếu cân Phòng Lab...`, 'process');
                    }
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Khởi động máy quét AI OCR...';
                }
                
                if (percent >= 8) {
                    if (!loggedMilestones.has('p8')) {
                        loggedMilestones.add('p8');
                        addLog(`Đang tối ưu hóa hình ảnh & khử nhiễu nhiễu ảnh nhiệt...`, 'process');
                    }
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang tối ưu hóa hình ảnh & khử nhiễu...';
                }
                
                if (percent >= 20) {
                    if (!loggedMilestones.has('p20')) {
                        loggedMilestones.add('p20');
                        addLog(`Nhận diện bố cục: Phát hiện 2 cột in nhiệt kết quả cân.`, 'process');
                    }
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang phân tích cấu trúc cột phiếu lab...';
                }
                
                if (percent >= 35) {
                    if (!loggedMilestones.has('p35')) {
                        loggedMilestones.add('p35');
                        addLog(`Phát hiện chữ viết tay: Mã hiệu 'DDKL-03', Số lô '1226003'.`, 'success');
                        addLog(`Đọc thông tin phần cứng: Cân phân tích METTLER TOLEDO MS204S.`, 'process');
                    }
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang nhận diện chữ viết tay & cấu hình...';
                }
                
                if (percent >= 50) {
                    if (!loggedMilestones.has('p50')) {
                        loggedMilestones.add('p50');
                        addLog(`Đang trích xuất dữ liệu khối lượng (20 chỉ tiêu)...`, 'process');
                    }
                }
                
                if (percent >= 50 && percent < 85) {
                    const pillsToFill = Math.min(20, Math.floor((percent - 50) / 1.75));
                    if (ocrProgressLabel) ocrProgressLabel.textContent = `Đang trích xuất dữ liệu khối lượng (${pillsToFill}/20)...`;
                    
                    for (let i = 0; i < pillsToFill; i++) {
                        const pillNum = i + 1;
                        const val = mockPillWeights[i];
                        const inputEl = document.getElementById(`w${pillNum}`);
                        const indicatorEl = document.getElementById(`ind-w${pillNum}`);
                        const ocrBox = document.getElementById(`box-w${pillNum}`);
                        
                        if (inputEl && inputEl.value === '') {
                            inputEl.value = val;
                            inputEl.classList.add('filled-highlight');
                            if (indicatorEl) indicatorEl.className = 'extraction-indicator success';
                            if (ocrBox) ocrBox.className = 'ocr-box success';
                            
                            if (pillNum % 5 === 1) {
                                addLog(`Trích xuất viên V${pillNum} đến V${Math.min(pillNum+4, 20)}: ${val}g`, 'process');
                            }
                        }
                    }
                }
                
                if (percent >= 85) {
                    if (!loggedMilestones.has('p85')) {
                        loggedMilestones.add('p85');
                        addLog(`Trích xuất thành công 20/20 khối lượng. Đang tính toán dữ liệu...`, 'success');
                    }
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang đối chiếu Dược Điển Việt Nam V...';
                }
                
                if (percent >= 92) {
                    if (!loggedMilestones.has('p92')) {
                        loggedMilestones.add('p92');
                        addLog(`Kiểm định Dược Điển: Trung bình = 0.256g | RSD = 0.82% (ĐẠT).`, 'success');
                    }
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang lưu trữ kết quả kiểm nghiệm...';
                }
                
                if (percent < 100) {
                    requestAnimationFrame(updatePhotoScan);
                } else {
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Hoàn tất quét phiếu cân lab!';
                    
                    for (let i = 0; i < 20; i++) {
                        const pillNum = i + 1;
                        const val = mockPillWeights[i];
                        const inputEl = document.getElementById(`w${pillNum}`);
                        const indicatorEl = document.getElementById(`ind-w${pillNum}`);
                        const ocrBox = document.getElementById(`box-w${pillNum}`);
                        if (inputEl && inputEl.value === '') {
                            inputEl.value = val;
                            inputEl.classList.add('filled-highlight');
                            if (indicatorEl) indicatorEl.className = 'extraction-indicator success';
                            if (ocrBox) ocrBox.className = 'ocr-box success';
                        }
                    }
                    
                    setTimeout(() => {
                        if (ocrProgressBox) ocrProgressBox.classList.add('hidden');
                        finishPhotoScanningProcess();
                        btnTabWord.removeAttribute('disabled');
                        btnTabPhoto.removeAttribute('disabled');
                        fileInput.removeAttribute('disabled');
                    }, 500);
                }
            }
            
            requestAnimationFrame(updatePhotoScan);
        }
    });

    function finishScanningProcess() {
        laserLine.classList.add('hidden');
        
        formStatusBadge.textContent = 'Hoàn tất';
        formStatusBadge.className = 'status-badge completed';
        consoleStatusDot.className = 'console-status-dot idle';

        isProcessing = false;
        setScanButtonState(true);
        btnResetScan.removeAttribute('disabled');
        templateButtons.forEach(btn => btn.removeAttribute('disabled'));
        fileInput.removeAttribute('disabled');

        btnFormClear.removeAttribute('disabled');
        btnFormSubmit.removeAttribute('disabled');

        addLog(`🎉 <strong>Autofill Process Completed!</strong> 10 fields synchronized.`, 'success');
        addLog(`Data verified by client schema. Ready to write to DB.`, 'success');
    }

    function finishPhotoScanningProcess() {
        photoLaserLine.classList.add('hidden');
        
        photoStatusBadge.textContent = 'Hoàn tất';
        photoStatusBadge.className = 'status-badge completed';
        consoleStatusDot.className = 'console-status-dot idle';

        isProcessing = false;
        setScanButtonState(true);
        btnResetPhoto.removeAttribute('disabled');
        btnTabWord.removeAttribute('disabled');
        fileInput.removeAttribute('disabled');

        btnPhotoClear.removeAttribute('disabled');
        btnSyncCoa.removeAttribute('disabled');

        let total = 0;
        mockPillWeights.forEach(w => total += parseFloat(w));
        const mean = (total / 20).toFixed(3);
        
        const rsdVal = "0.82%";

        valMean.textContent = `${mean} g`;
        valRsd.textContent = rsdVal;
        
        valResult.textContent = 'Đạt yêu cầu';
        valResult.style.color = 'var(--success)';
        
        document.getElementById('uniformity-card-glow').classList.add('active-glow');

        addLog(`🎉 <strong>AI OCR Calculations Complete!</strong>`, 'success');
        addLog(`Uniformity results: Average = <strong>${mean}g</strong> | RSD% = <strong>${rsdVal}</strong>`, 'success');
        addLog(`All 20 tablets are within the Pharmacopoeia limit (±5%). Verdict: <strong>PASSED</strong>.`, 'success');
        addLog(`Ready to synchronize and generate DRP INTER COA Report.`, 'success');
    }

    if (btnFormClear) {
        btnFormClear.addEventListener('click', () => {
            if (isProcessing) return;
            resetFormInputs();
            addLog('HTML Form cleared by user.', 'system');
        });
    }

    if (btnFormSubmit) {
        btnFormSubmit.addEventListener('click', () => {
            if (isProcessing) return;
            
            const wordFormData = {
                trade_name: sanitizeFieldValue(document.getElementById('trade_name')?.value || ''),
                active_ingredient: sanitizeFieldValue(document.getElementById('active_ingredient')?.value || ''),
                strength: sanitizeFieldValue(document.getElementById('strength')?.value || ''),
                dosage_form: sanitizeFieldValue(document.getElementById('dosage_form')?.value || ''),
                manufacturer: sanitizeFieldValue(document.getElementById('manufacturer')?.value || ''),
                batch_number: sanitizeFieldValue(document.getElementById('batch_number')?.value || ''),
                registration_number: sanitizeFieldValue(document.getElementById('registration_number')?.value || ''),
                mfg_date: sanitizeFieldValue(document.getElementById('mfg_date')?.value || ''),
                exp_date: sanitizeFieldValue(document.getElementById('exp_date')?.value || ''),
                indications: sanitizeFieldValue(document.getElementById('indications')?.value || ''),
                scan_date: new Date().toLocaleDateString('vi-VN'),
                form_type: 'word_extraction'
            };
            
            sessionStorage.setItem('word_form_data', JSON.stringify(wordFormData));
            
            addLog('✅ Word Form data saved (cleaned format)', 'success');
            addLog('📋 Dữ liệu sản phẩm đã được lưu không có định dạng', 'info');
            
            successModal.classList.remove('hidden');
            addLog('Form submission event triggered. Payload sent successfully.', 'success');
        });
    }

    if (btnPhotoClear) {
        btnPhotoClear.addEventListener('click', () => {
            if (isProcessing) return;
            resetPhotoFormInputs();
            addLog('Weight Uniformity Form cleared by user.', 'system');
        });
    }

    function sanitizeFieldValue(value) {
        if (!value) return '';
        let clean = value.replace(/<[^>]*>/g, '');
        clean = clean.replace(/\n\s+/g, ' ').trim();
        return clean;
    }

    if (btnSyncCoa) {
        btnSyncCoa.addEventListener('click', () => {
            if (isProcessing) return;

            addLog('📋 Đang chuyển hướng đến 20 phiếu kiểm nghiệm...', 'process');
            
            setTimeout(() => {
                window.location.href = '/coa/';
            }, 800);
        });
    }

    if (btnModalClose) {
        btnModalClose.addEventListener('click', () => {
            successModal.classList.add('hidden');
            resetToInitialState();
        });
    }

    if (successModal) {
        successModal.addEventListener('click', (e) => {
            if (e.target === successModal) {
                successModal.classList.add('hidden');
                resetToInitialState();
            }
        });
    }
});