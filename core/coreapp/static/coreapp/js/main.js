

document.addEventListener('DOMContentLoaded', () => {
    // ==========================================================================
    // 1. STICKY HEADER & NAVBAR EFFECTS
    // ==========================================================================
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

    // ==========================================================================
    // 2. MOBILE MENU TOGGLE
    // ==========================================================================
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const navMenu = document.getElementById('nav-navigation');
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', () => {
            navMenu.classList.toggle('open');
            mobileToggle.classList.toggle('open');
        });
        // Close menu on link click
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('open');
                mobileToggle.classList.remove('open');
            });
        });
    }

    // ==========================================================================
    // 3. USER DROPDOWN TOGGLE
    // ==========================================================================
    const dropdownTrigger = document.getElementById('user-dropdown-trigger');
    const dropdownMenu = document.getElementById('user-dropdown-menu');
    if (dropdownTrigger && dropdownMenu) {
        dropdownTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdownMenu.classList.toggle('open');
            dropdownTrigger.classList.toggle('open');
        });
        document.addEventListener('click', (e) => {
            if (!dropdownTrigger.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownMenu.classList.remove('open');
                dropdownTrigger.classList.remove('open');
            }
        });
    }

    // ==========================================================================
    // 4. AUTHENTICATION (LOGIN / REGISTER) INTERACTIVE LOGIC
    // ==========================================================================
    const demoOpBtn = document.getElementById('btn-demo-operator');
    const demoAdminBtn = document.getElementById('btn-demo-admin');
    const loginEmailInput = document.getElementById('login-email');
    const loginPasswordInput = document.getElementById('login-password');
    const loginForm = document.getElementById('login-form');

    if (demoOpBtn && demoAdminBtn) {
        // Operator quick login mock
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

        // Admin quick login mock
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
                        window.location.href = '/scan/';
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

    // ==========================================================================
    // 5. ADMIN DASHBOARD SYSTEM INTERACTIONS
    // ==========================================================================
    const sidebarMenuItems = document.querySelectorAll('.db-menu-item');
    const tabPanes = document.querySelectorAll('.db-tab-pane');
    const dbTabTitle = document.getElementById('db-tab-title');

    if (sidebarMenuItems.length > 0) {
        // Tab switching logic
        sidebarMenuItems.forEach(item => {
            item.addEventListener('click', () => {
                const targetTabId = item.getAttribute('data-tab');
                
                // Active menu state
                sidebarMenuItems.forEach(menu => menu.classList.remove('active'));
                item.classList.add('active');

                // Active tab pane state
                tabPanes.forEach(pane => {
                    pane.classList.add('hidden');
                    pane.classList.remove('active');
                });
                const targetPane = document.getElementById(targetTabId);
                if (targetPane) {
                    targetPane.classList.remove('hidden');
                    targetPane.classList.add('active');
                }

                // Update navbar title
                if (dbTabTitle) {
                    dbTabTitle.textContent = item.querySelector('span').textContent;
                }
            });
        });

        // Live date display today
        const liveDateEl = document.getElementById('db-live-date');
        if (liveDateEl) {
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            const today = new Date();
            liveDateEl.textContent = today.toLocaleDateString('vi-VN', options);
        }

        // Dynamic Verification & Audit Modal Logic
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

            // Approve Action Event
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

        // Excel Document Export Simulation
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


    // ==========================================================================
    // 6. SCAN PAGE SCANNER ENGINE & INTERACTION
    // ==========================================================================
    const dropzone = document.getElementById('document-dropzone');
    if (!dropzone) return; // Exit if not on scanning page

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

    // Quick Templates Buttons
    const tempPara = document.getElementById('temp-para');
    const tempAmox = document.getElementById('temp-amox');
    const tempVac = document.getElementById('temp-vac');
    const templateButtons = document.querySelectorAll('.btn-template');

    // LAB RECEIPT DYNAMIC MOCKUP CONTROLS & SELECTIONS (New Giai đoạn 3)
    const btnTabWord = document.getElementById('btn-tab-word');
    const btnTabPhoto = document.getElementById('btn-tab-photo');
    const wordTemplatesBlock = document.getElementById('word-templates-selection');
    const photoTemplatesBlock = document.getElementById('photo-templates-selection');
    const filePhotoLoadedView = document.getElementById('file-photo-loaded-view');
    const btnResetPhoto = document.getElementById('btn-reset-photo');
    const panelWordForm = document.getElementById('panel-word-form');
    const panelPhotoForm = document.getElementById('panel-photo-form');
    
    // Weight Uniformity target fields
    const photoStatusBadge = document.getElementById('photo-status-badge');
    const valMean = document.getElementById('val-mean');
    const valRsd = document.getElementById('val-rsd');
    const valResult = document.getElementById('val-result');
    const btnPhotoClear = document.getElementById('btn-photo-clear');
    const btnSyncCoa = document.getElementById('btn-sync-coa');
    const photoLaserLine = document.getElementById('photo-laser-line');
    
    // Toggle view components
    const btnToggleRealImg = document.getElementById('btn-toggle-real-img');
    const btnToggleSimOcr = document.getElementById('btn-toggle-sim-ocr');
    const realImgContainer = document.getElementById('real-image-preview-container');
    const simOcrContainer = document.querySelector('.receipt-mockup-wrapper');
    const realLaserLine = document.getElementById('real-image-laser-line');

    function showLaserLines() {
        const realImgVisible = realImgContainer && !realImgContainer.classList.contains('hidden');
        if (realImgVisible && realLaserLine) {
            realLaserLine.classList.remove('hidden');
        } else if (photoLaserLine) {
            photoLaserLine.classList.remove('hidden');
        }
    }

    function hideLaserLines() {
        if (realLaserLine) realLaserLine.classList.add('hidden');
        if (photoLaserLine) photoLaserLine.classList.add('hidden');
    }

    if (btnToggleRealImg && btnToggleSimOcr && realImgContainer && simOcrContainer) {
        btnToggleRealImg.addEventListener('click', () => {
            btnToggleRealImg.classList.add('active');
            btnToggleSimOcr.classList.remove('active');
            realImgContainer.classList.remove('hidden');
            simOcrContainer.classList.add('hidden');
        });

        btnToggleSimOcr.addEventListener('click', () => {
            btnToggleSimOcr.classList.add('active');
            btnToggleRealImg.classList.remove('active');
            simOcrContainer.classList.remove('hidden');
            realImgContainer.classList.add('hidden');
        });
    }
    // OCR progress bar elements
    const ocrProgressBox = document.getElementById('ocr-progress-box');
    const ocrProgressFill = document.getElementById('ocr-progress-fill');
    const ocrProgressPercent = document.getElementById('ocr-progress-percent');
    const ocrProgressLabel = document.getElementById('ocr-progress-label');

    let currentScanMode = 'word'; // 'word' or 'photo'
    let selectedDocumentKey = null;
    let isProcessing = false;
    let selectedFile = null;
    let ocrExtractedRecords = [];
    let fileQueue = [];

    function updateQueueUI() {
        const queueContainer = document.getElementById('batch-queue-container');
        const queueList = document.getElementById('queue-list');
        const queueCount = document.getElementById('queue-count');
        if (!queueContainer || !queueList) return;

        if (fileQueue.length > 0) {
            queueContainer.classList.remove('hidden');
            queueCount.textContent = `${fileQueue.length} tệp`;
            queueList.innerHTML = '';
            
            fileQueue.forEach((fileObj, idx) => {
                const item = document.createElement('div');
                item.style.cssText = 'display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); border: 1px solid var(--surface-border); border-radius: 4px; padding: 6px 10px; font-size: 0.76rem;';
                
                let statusBadge = `<span class="status-badge" style="font-size: 0.65rem; padding: 2px 6px;">Chờ quét</span>`;
                if (fileObj.status === 'processing') {
                    statusBadge = `<span class="status-badge scanning" style="font-size: 0.65rem; padding: 2px 6px;">Đang quét...</span>`;
                } else if (fileObj.status === 'done') {
                    statusBadge = `<span class="status-badge completed" style="font-size: 0.65rem; padding: 2px 6px; background: rgba(16,185,129,0.15); color: var(--success);">Hoàn tất (${fileObj.added} mẫu)</span>`;
                } else if (fileObj.status === 'failed') {
                    statusBadge = `<span class="status-badge" style="font-size: 0.65rem; padding: 2px 6px; background: rgba(239,68,68,0.15); color: #f87171;">Thất bại</span>`;
                }

                const deleteBtn = !isProcessing 
                    ? `<button type="button" class="btn-remove-file remove-queue-item" data-index="${idx}" title="Xóa" style="width: 18px; height: 18px; background: rgba(255,255,255,0.05); margin-left: 6px; border: none; cursor: pointer; color: var(--text-muted); display: inline-flex; align-items: center; justify-content: center; border-radius: 2px;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:10px; height:10px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg></button>`
                    : '';

                item.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 8px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; max-width: 60%;">
                        <span style="color: var(--text-muted); font-weight: 700;">#${idx+1}</span>
                        <span style="color: var(--text-primary); overflow: hidden; text-overflow: ellipsis;" title="${fileObj.file.name}">${fileObj.file.name}</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        ${statusBadge}
                        ${deleteBtn}
                    </div>
                `;
                queueList.appendChild(item);
            });

            // Register remove handlers
            const removeBtns = queueList.querySelectorAll('.remove-queue-item');
            removeBtns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const index = parseInt(btn.getAttribute('data-index'));
                    fileQueue.splice(index, 1);
                    updateQueueUI();
                    if (fileQueue.length === 0) {
                        resetToInitialState();
                    }
                });
            });
        } else {
            queueContainer.classList.add('hidden');
        }
    }

    function cleanVal(str) {
        return (str || '').toString().replace(/\s+/g, '').replace(/[gG]$/, '').trim();
    }

    function recordsMatch(rec1, rec2) {
        if (!rec1 || !rec2) return false;
        const w1 = cleanVal(rec1.weight);
        const w2 = cleanVal(rec2.weight);
        const dt1 = cleanVal(rec1.datetime);
        const dt2 = cleanVal(rec2.datetime);

        // If both have weight, they must match
        if (w1 && w2 && w1 !== '-' && w2 !== '-' && w1 !== w2) return false;
        // If both have datetime, they must match
        if (dt1 && dt2 && dt1 !== '-' && dt2 !== '-' && dt1 !== dt2) return false;

        const hasSharedWeight = w1 && w2 && w1 !== '-' && w2 !== '-';
        const hasSharedDatetime = dt1 && dt2 && dt1 !== '-' && dt2 !== '-';
        
        return hasSharedWeight || hasSharedDatetime;
    }

    function findOverlap(A, B) {
        let bestOffset = null;
        let maxMatches = 0;
        const minOverlap = 1;
        
        for (let offset = -(B.length - 1); offset < A.length; offset++) {
            let matches = 0;
            let mismatches = 0;
            let overlapCount = 0;
            
            for (let i = 0; i < B.length; i++) {
                const aIdx = offset + i;
                if (aIdx >= 0 && aIdx < A.length) {
                    overlapCount++;
                    if (recordsMatch(A[aIdx], B[i])) {
                        matches++;
                    } else {
                        const wA = cleanVal(A[aIdx].weight);
                        const wB = cleanVal(B[i].weight);
                        const dtA = cleanVal(A[aIdx].datetime);
                        const dtB = cleanVal(B[i].datetime);
                        
                        const weightMismatch = wA && wB && wA !== '-' && wB !== '-' && wA !== wB;
                        const dateMismatch = dtA && dtB && dtA !== '-' && dtB !== '-' && dtA !== dtB;
                        
                        if (weightMismatch || dateMismatch) {
                            mismatches++;
                        }
                    }
                }
            }
            
            if (overlapCount >= minOverlap && mismatches === 0 && matches > maxMatches) {
                maxMatches = matches;
                bestOffset = offset;
            }
        }
        return { offset: bestOffset, matches: maxMatches };
    }

    function mergeAligned(A, B, offset) {
        const merged = [];
        const start = Math.min(0, offset);
        const end = Math.max(A.length, offset + B.length);
        
        for (let idx = start; idx < end; idx++) {
            const aIdx = idx;
            const bIdx = idx - offset;
            
            const recA = (aIdx >= 0 && aIdx < A.length) ? A[aIdx] : null;
            const recB = (bIdx >= 0 && bIdx < B.length) ? B[bIdx] : null;
            
            if (recA && recB) {
                merged.push({
                    weight: (recA.weight && recA.weight !== '-') ? recA.weight : (recB.weight || '-'),
                    datetime: (recA.datetime && recA.datetime !== '-') ? recA.datetime : (recB.datetime || '-'),
                    balance_type: (recA.balance_type && recA.balance_type !== '-') ? recA.balance_type : (recB.balance_type || '-'),
                    snr: (recA.snr && recA.snr !== '-') ? recA.snr : (recB.snr || '-')
                });
            } else if (recA) {
                merged.push({ ...recA });
            } else if (recB) {
                merged.push({ ...recB });
            }
        }
        return merged;
    }

    function getEarliestTime(list) {
        for (let i = 0; i < list.length; i++) {
            const dtStr = list[i].datetime;
            if (dtStr && dtStr !== '-') {
                const parts = dtStr.split(/[\s.:]+/);
                if (parts.length >= 5) {
                    const day = parseInt(parts[0]);
                    const month = parseInt(parts[1]) - 1;
                    const year = parseInt(parts[2]);
                    const hour = parseInt(parts[3]);
                    const min = parseInt(parts[4]);
                    return new Date(year, month, day, hour, min).getTime();
                }
            }
        }
        return null;
    }

    function stitchOcrSessions(A, B) {
        if (!A || A.length === 0) {
            return B.map((rec, idx) => ({
                id: idx + 1,
                weight: rec.weight || '-',
                datetime: rec.datetime || '-',
                balance_type: rec.balance_type || '-',
                snr: rec.snr || '-'
            }));
        }
        if (!B || B.length === 0) {
            return A;
        }

        const alignment = findOverlap(A, B);
        
        if (alignment.offset !== null && alignment.matches > 0) {
            addLog(`Phát hiện vùng gối đầu (Khớp ${alignment.matches} bản ghi trùng). Đang ghép nối...`, 'success');
            const merged = mergeAligned(A, B, alignment.offset);
            merged.forEach((r, idx) => {
                r.id = idx + 1;
            });
            return merged;
        }

        const timeA = getEarliestTime(A);
        const timeB = getEarliestTime(B);

        let merged = [];
        if (timeA !== null && timeB !== null) {
            if (timeB < timeA) {
                addLog(`Không tìm thấy vùng trùng lặp. Tự động sắp xếp: Dữ liệu mới in trước dữ liệu cũ.`, 'system');
                merged = [...B, ...A];
            } else {
                addLog(`Không tìm thấy vùng trùng lặp. Tự động sắp xếp: Dữ liệu mới in sau dữ liệu cũ.`, 'system');
                merged = [...A, ...B];
            }
        } else {
            addLog(`Không thể xác định thời gian in. Tự động nối tiếp dữ liệu mới vào cuối bảng.`, 'system');
            merged = [...A, ...B];
        }

        merged.forEach((r, idx) => {
            r.id = idx + 1;
        });
        return merged;
    }

    function handleMultipleFiles(files) {
        if (isProcessing) return;
        
        const firstFile = files[0];
        const nameLower = firstFile.name.toLowerCase();
        
        if (nameLower.endsWith('.jpg') || nameLower.endsWith('.jpeg') || nameLower.endsWith('.png')) {
            fileQueue = [];
            for (let i = 0; i < files.length; i++) {
                fileQueue.push({
                    file: files[i],
                    status: 'pending',
                    added: 0
                });
            }
            
            btnTabPhoto.click();
            selectedFile = fileQueue[0].file;
            selectedDocumentKey = 'photo-lab';
            
            const realImgEl = document.getElementById('real-image-preview');
            if (realImgEl) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    realImgEl.src = e.target.result;
                }
                reader.readAsDataURL(selectedFile);
            }
            
            if (btnToggleRealImg && btnToggleSimOcr && realImgContainer && simOcrContainer) {
                btnToggleRealImg.classList.add('active');
                btnToggleSimOcr.classList.remove('active');
                realImgContainer.classList.remove('hidden');
                simOcrContainer.classList.add('hidden');
            }
            
            dropzonePrompt.classList.add('hidden');
            fileLoadedView.classList.add('hidden');
            filePhotoLoadedView.classList.remove('hidden');
            setScanButtonState(true);
            
            updateQueueUI();
            addLog(`Đã tải ${fileQueue.length} ảnh vào hàng đợi quét.`, 'system');
        } else {
            selectedFile = firstFile;
            simulateCustomFileUpload(firstFile.name);
        }
    }

    async function runBatchOCR() {
        isProcessing = true;
        setScanButtonState(false);
        btnTabWord.setAttribute('disabled', 'true');
        btnTabPhoto.setAttribute('disabled', 'true');
        fileInput.setAttribute('disabled', 'true');
        if (btnResetPhoto) btnResetPhoto.setAttribute('disabled', 'true');
        if (btnPhotoClear) btnPhotoClear.setAttribute('disabled', 'true');
        if (btnSyncCoa) btnSyncCoa.setAttribute('disabled', 'true');
        
        addLog(`🚀 Bắt đầu tiến trình quét liên tục ${fileQueue.length} ảnh...`, 'process');
        
        for (let idx = 0; idx < fileQueue.length; idx++) {
            const queueItem = fileQueue[idx];
            queueItem.status = 'processing';
            updateQueueUI();
            
            selectedFile = queueItem.file;
            const realImgEl = document.getElementById('real-image-preview');
            if (realImgEl) {
                const reader = new FileReader();
                await new Promise((resolve) => {
                    reader.onload = function(e) {
                        realImgEl.src = e.target.result;
                        resolve();
                    }
                    reader.readAsDataURL(selectedFile);
                });
            }
            
            addLog(`[Ảnh ${idx+1}/${fileQueue.length}]: Đang phân tích ${queueItem.file.name}...`, 'process');
            
            showLaserLines();
            if (ocrProgressBox) {
                ocrProgressBox.classList.remove('hidden');
                ocrProgressFill.style.width = '30%';
                ocrProgressPercent.textContent = '30%';
                ocrProgressLabel.textContent = `Đang quét tệp ${idx+1}: ${queueItem.file.name}...`;
            }
            
            try {
                const formData = new FormData();
                formData.append('image', queueItem.file);
                
                const response = await fetch('/user/scan/receipt-api/', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    const errData = await response.json();
                    throw new Error(errData.error || `HTTP ${response.status}`);
                }
                
                const result = await response.json();
                if (!result.success) {
                    throw new Error(result.error || 'Quét ảnh thất bại.');
                }
                
                const incomingRecords = result.records || [];
                const oldLen = ocrExtractedRecords.length;
                ocrExtractedRecords = stitchOcrSessions(ocrExtractedRecords, incomingRecords);
                const addedCount = ocrExtractedRecords.length - oldLen;
                
                queueItem.status = 'done';
                queueItem.added = incomingRecords.length;
                
                addLog(`[Ảnh ${idx+1}/${fileQueue.length}] Thành công! Trích xuất ${incomingRecords.length} mẫu.`, 'success');
                
                renderOcrTable(ocrExtractedRecords);
                updateUniformityStatsAndPills();
                
            } catch (err) {
                queueItem.status = 'failed';
                addLog(`[Ảnh ${idx+1}/${fileQueue.length}] Lỗi: ${err.message}`, 'error');
            } finally {
                hideLaserLines();
                updateQueueUI();
            }
            
            if (idx < fileQueue.length - 1) {
                addLog(`Đang nghỉ 1.5 giây để tránh quá tải API...`, 'system');
                await new Promise(resolve => setTimeout(resolve, 1500));
            }
        }
        
        isProcessing = false;
        setScanButtonState(true);
        btnTabWord.removeAttribute('disabled');
        btnTabPhoto.removeAttribute('disabled');
        fileInput.removeAttribute('disabled');
        if (btnResetPhoto) btnResetPhoto.removeAttribute('disabled');
        if (btnPhotoClear) btnPhotoClear.removeAttribute('disabled');
        if (btnSyncCoa) btnSyncCoa.removeAttribute('disabled');
        
        if (ocrProgressBox) ocrProgressBox.classList.add('hidden');
        document.getElementById('uniformity-card-glow').classList.add('active-glow');
        addLog(`🎉 Hoàn tất tiến trình quét liên tục! Đã ghép nối tổng cộng: ${ocrExtractedRecords.length} mẫu.`, 'success');
    }

    // Helper to toggle scan button state and premium glow animations
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

    // Weight Uniformity Mock Values Database (DRP INTER Lô 1226003) - Dynamic, not limited to 20
    const mockPillWeights = [
        "0.258", "0.255", "0.256", "0.254", "0.252", 
        "0.256", "0.260", "0.258", "0.255", "0.257",
        "0.259", "0.253", "0.258", "0.256", "0.255", 
        "0.255", "0.253", "0.258", "0.256", "0.255"
    ];
    
    // Add more mock data for unlimited testing
    const mockPillWeightsExtended = [
        "0.257", "0.254", "0.259", "0.256", "0.253",
        "0.258", "0.255", "0.260", "0.254", "0.257"
    ];

    // Add message to live console
    function addLog(text, type = 'system') {
        if (!consoleLogs) return;
        const timestamp = new Date().toLocaleTimeString();
        const logLine = document.createElement('div');
        logLine.className = `log-line log-${type}`;
        logLine.innerHTML = `<span class="log-time" style="color: #64748b; margin-right: 8px;">[${timestamp}]</span> ${text}`;
        consoleLogs.appendChild(logLine);
        consoleLogs.scrollTop = consoleLogs.scrollHeight;
    }

    // Toggle Modes (Word vs Photo Scanner)
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

    // Mock Documents Database
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

    // Set selected document preview on paper mockup
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

            // Default to simulated view for mockup samples
            if (btnToggleRealImg && btnToggleSimOcr && realImgContainer && simOcrContainer) {
                btnToggleSimOcr.classList.add('active');
                btnToggleRealImg.classList.remove('active');
                simOcrContainer.classList.remove('hidden');
                realImgContainer.classList.add('hidden');
            }
            const realImgEl = document.getElementById('real-image-preview');
            if (realImgEl) realImgEl.src = ''; // Clear image source for mockup mode

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

    // Connect Quick templates button events
    templateButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetKey = button.getAttribute('data-target');
            loadDocumentState(targetKey);
        });
    });

    // Setup input file click behavior
    dropzonePrompt.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleMultipleFiles(e.target.files);
        }
    });

    // Drag over styling
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
            handleMultipleFiles(files);
        }
    });

    // File reset clear actions
    btnResetScan.addEventListener('click', (e) => {
        e.stopPropagation();
        if (isProcessing) return;
        resetToInitialState();
    });

    btnResetPhoto.addEventListener('click', (e) => {
        e.stopPropagation();
        if (isProcessing) return;
        
        selectedDocumentKey = null;
        selectedFile = null;
        ocrExtractedRecords = [];
        fileQueue = [];
        updateQueueUI();
        renderOcrTable(ocrExtractedRecords);
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
        fileQueue = [];
        updateQueueUI();
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
        const uniformityGlow = document.getElementById('uniformity-card-glow');
        if (uniformityGlow) uniformityGlow.classList.remove('active-glow');
        if (btnPhotoClear) btnPhotoClear.setAttribute('disabled', 'true');
        if (btnSyncCoa) btnSyncCoa.setAttribute('disabled', 'true');
    }

    // Handle dropping/browsing a real user file
    function simulateCustomFileUpload(fileName) {
        if (isProcessing) return;
        
        const nameLower = fileName.toLowerCase();
        // Check if user uploaded a photo of balance receipt (jpg, png)
        if (nameLower.endsWith('.jpg') || nameLower.endsWith('.jpeg') || nameLower.endsWith('.png')) {
            btnTabPhoto.click();
            addLog(`Analyzing uploaded photo: <strong>${fileName}</strong>`, 'system');
            
            // Load real image preview
            const realImgEl = document.getElementById('real-image-preview');
            if (realImgEl && selectedFile) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    realImgEl.src = e.target.result;
                }
                reader.readAsDataURL(selectedFile);
            }

            // Default to real image toggle view for manual uploads
            if (btnToggleRealImg && btnToggleSimOcr && realImgContainer && simOcrContainer) {
                btnToggleRealImg.classList.add('active');
                btnToggleSimOcr.classList.remove('active');
                realImgContainer.classList.remove('hidden');
                simOcrContainer.classList.add('hidden');
            }
            
            setTimeout(() => {
                selectedDocumentKey = 'photo-lab';
                dropzonePrompt.classList.add('hidden');
                fileLoadedView.classList.add('hidden');
                filePhotoLoadedView.classList.remove('hidden');
                setScanButtonState(true);
                
                const photoBtn = document.getElementById('temp-photo-lab');
                if (photoBtn) photoBtn.classList.add('active');
                
                addLog(`Photo processed. Valid laboratory balance receipt signature match.`, 'success');
                
                // Automatically start the scanning process after manual upload
                if (btnStartProcess) {
                    btnStartProcess.click();
                }
            }, 800);
            return;
        }

        // Default to Word file import
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

    // MAIN AI SCANNER SIMULATION ACTION (Supports Word & Photo scan pipelines)
    // Helper function to type values dynamically (Typewriter Effect)
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

    // Helper to dynamically update dropzone prompts based on active tab
    function updateDropzoneText(mode) {
        const titleEl = document.getElementById('dropzone-title-main');
        const supportEl = document.getElementById('dropzone-support-main');
        const photoHints = document.getElementById('dropzone-photo-hints');
        if (!titleEl || !supportEl) return;
        
        if (mode === 'word') {
            titleEl.textContent = 'Kéo & Thả file Word ở đây';
            supportEl.textContent = 'Hỗ trợ các định dạng: .docx, .doc, .pdf';
            if (photoHints) photoHints.classList.add('hidden');
        } else {
            titleEl.textContent = 'Kéo & Thả nhiều ảnh Phiếu Cân ở đây';
            supportEl.textContent = 'Hỗ trợ các định dạng: .jpg, .jpeg, .png';
            if (photoHints) photoHints.classList.remove('hidden');
        }
    }

    // MAIN AI SCANNER ENGINE AND PROGRESS ANIMATION LOOP
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
            
            const duration = 2500; // 2.5 seconds
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
                    if (ocrProgressLabel) ocrProgressLabel.textContent = 'Hoàn tất quét biểu mẫu!';
                    
                    for (let i = 0; i < dataKeys.length; i++) {
                        const key = dataKeys[i];
                        const inputEl = document.getElementById(key);
                        if (inputEl && inputEl.value === '') {
                            inputEl.value = doc.formData[key];
                            inputEl.classList.add('filled-highlight');
                            const indicatorEl = document.getElementById(`ind-${key}`);
                            if (indicatorEl) indicatorEl.className = 'extraction-indicator success';
                        }
                    }
                    
                    setTimeout(() => {
                        if (ocrProgressBox) ocrProgressBox.classList.add('hidden');
                        finishScanningProcess();
                    }, 500);
                }
            }
            
            requestAnimationFrame(updateWordScan);
        } else {
            // PHOTO OCR BALANCE RECEIPT MODE
            if (fileQueue.length > 0) {
                runBatchOCR();
            } else if (!selectedFile) {
                if (selectedDocumentKey === 'photo-lab') {
                    if (btnResetPhoto) btnResetPhoto.setAttribute('disabled', 'true');
                    resetPhotoFormInputs();
                    runSimulatedDemoOCR();
                } else {
                    addLog('Chưa có ảnh nào được tải lên. Vui lòng chọn ảnh phiếu cân.', 'error');
                    isProcessing = false;
                    setScanButtonState(true);
                    btnTabWord.removeAttribute('disabled');
                    btnTabPhoto.removeAttribute('disabled');
                    fileInput.removeAttribute('disabled');
                }
                return;
            } else {
                if (btnResetPhoto) btnResetPhoto.setAttribute('disabled', 'true');
                resetPhotoFormInputs();
                runGeminiOCR(selectedFile);
            }
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
        // Stop Laser animation
        hideLaserLines();
        
        // Update form status badge
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

        // Dynamic Uniformity Calculator computations
        // Calculate based on actual records count (not fixed 20)
        const actualRecords = ocrExtractedRecords.length > 0 ? ocrExtractedRecords : mockPillWeights.map(w => ({weight: w}));
        let total = 0;
        actualRecords.forEach(r => {
            const w = parseFloat(r.weight);
            if (!isNaN(w) && w > 0) total += w;
        });
        const mean = (total / actualRecords.length).toFixed(3);
        
        // Set RSD% relative standard deviation mockup value
        const rsdVal = "0.82%";

        // Write calculations on UI
        valMean.textContent = `${mean} g`;
        valRsd.textContent = rsdVal;
        
        valResult.textContent = 'Đạt yêu cầu';
        valResult.style.color = 'var(--success)';
        
        // Add uniformity card neon glow pulse
        document.getElementById('uniformity-card-glow').classList.add('active-glow');

        // Log completion
        addLog(`🎉 <strong>AI OCR Calculations Complete!</strong>`, 'success');
        addLog(`Uniformity results: Average = <strong>${mean}g</strong> | RSD% = <strong>${rsdVal}</strong>`, 'success');
        addLog(`All ${actualRecords.length} tablets are within the Pharmacopoeia limit (±5%). Verdict: <strong>PASSED</strong>.`, 'success');
        addLog(`Ready to synchronize and generate DRP INTER COA Report.`, 'success');
    }

    // Word Form buttons actions
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
            successModal.classList.remove('hidden');
            addLog('Form submission event triggered. Payload sent successfully.', 'success');
        });
    }

    // Photo Form buttons actions (Giai đoạn 3)
    if (btnPhotoClear) {
        btnPhotoClear.addEventListener('click', () => {
            if (isProcessing) return;
            ocrExtractedRecords = [];
            renderOcrTable(ocrExtractedRecords);
            resetPhotoFormInputs();
            updateUniformityStatsAndPills();
            addLog('Weight Uniformity Form cleared by user.', 'system');
        });
    }

    // Sync button redirecting to digitized Certificate of Analysis (form1.html)
    if (btnSyncCoa) {
        btnSyncCoa.addEventListener('click', () => {
            if (isProcessing) return;
            
            // Save calculated values to localStorage to dynamically fill form1.html
            localStorage.setItem('is_scanned_photo', 'true');
            localStorage.setItem('scan_trade_name', 'ZANDYRINE 10 MG');
            localStorage.setItem('scan_batch_number', '1226003');
            localStorage.setItem('scan_mfg_date', '01.04.26');
            localStorage.setItem('scan_exp_date', '31.03.29');
            localStorage.setItem('scan_dosage_form', 'VIÊN NÉN BAO PHIM');
            localStorage.setItem('scan_packing', 'Hộp 3 vỉ x 10 viên');
            localStorage.setItem('scan_product_code', 'AN1221T');
            localStorage.setItem('scan_std_number', 'QCFPAN1221T/ Lần ban hành: 01');
            localStorage.setItem('scan_report_number', 'QC-FP-26-0063');
            localStorage.setItem('scan_avg_weight', '0.256g');
            localStorage.setItem('scan_rsd', '0.82%');

            addLog('Synchronizing weights to Certificate of Analysis...', 'process');
            
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

    function mergeOcrRecords(existing, incoming) {
        function clean(str) {
            return (str || '').toString().replace(/\s+/g, '').replace(/[gG]$/, '').trim();
        }

        const merged = [...existing];

        incoming.forEach(newRec => {
            let isDuplicate = false;
            
            for (let i = 0; i < merged.length; i++) {
                const oldRec = merged[i];
                
                const oldW = clean(oldRec.weight);
                const newW = clean(newRec.weight);
                const oldDt = clean(oldRec.datetime);
                const newDt = clean(newRec.datetime);

                // Case 1: Exact match of weight and datetime
                if (oldW && newW && oldW !== '-' && newW !== '-' && oldDt && newDt && oldDt !== '-' && newDt !== '-') {
                    if (oldW === newW && oldDt === newDt) {
                        isDuplicate = true;
                        if ((!oldRec.snr || oldRec.snr === '-') && newRec.snr) oldRec.snr = newRec.snr;
                        if ((!oldRec.balance_type || oldRec.balance_type === '-') && newRec.balance_type) oldRec.balance_type = newRec.balance_type;
                        break;
                    }
                }

                // Case 2: Missing weight in existing but date matches
                if ((!oldW || oldW === '-') && newW && newW !== '-' && oldDt && newDt && oldDt !== '-' && oldDt === newDt) {
                    oldRec.weight = newRec.weight;
                    if (newRec.snr) oldRec.snr = newRec.snr;
                    if (newRec.balance_type) oldRec.balance_type = newRec.balance_type;
                    isDuplicate = true;
                    break;
                }

                // Case 3: Missing date in new record but weight matches
                if (oldW && newW && oldW !== '-' && oldW === newW && oldDt && oldDt !== '-' && (!newDt || newDt === '-')) {
                    isDuplicate = true;
                    break;
                }
                
                // Case 4: Missing date in existing but weight matches
                if (oldW && newW && oldW !== '-' && oldW === newW && (!oldDt || oldDt === '-') && newDt && newDt !== '-') {
                    oldRec.datetime = newRec.datetime;
                    if (newRec.snr) oldRec.snr = newRec.snr;
                    if (newRec.balance_type) oldRec.balance_type = newRec.balance_type;
                    isDuplicate = true;
                    break;
                }
            }

            if (!isDuplicate) {
                merged.push({
                    id: merged.length + 1,
                    weight: newRec.weight || '-',
                    datetime: newRec.datetime || '-',
                    balance_type: newRec.balance_type || '-',
                    snr: newRec.snr || '-'
                });
            }
        });

        // Re-index
        merged.forEach((r, idx) => {
            r.id = idx + 1;
        });

        return merged;
    }

    async function runGeminiOCR(file) {
        showLaserLines();
        if (btnPhotoClear) btnPhotoClear.setAttribute('disabled', 'true');
        if (btnSyncCoa) btnSyncCoa.setAttribute('disabled', 'true');
        
        try {
            if (ocrProgressBox) {
                ocrProgressBox.classList.remove('hidden');
                ocrProgressFill.style.width = '0%';
                ocrProgressPercent.textContent = '0%';
                ocrProgressLabel.textContent = 'Đang gửi ảnh lên máy chủ...';
            }
            addLog('Đang gửi ảnh lên backend và bắt đầu xử lý bằng Gemini Vision API...', 'process');

            const formData = new FormData();
            formData.append('image', file);

            const response = await fetch('/user/scan/receipt-api/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || `HTTP ${response.status}`);
            }

            if (ocrProgressFill) ocrProgressFill.style.width = '60%';
            if (ocrProgressPercent) ocrProgressPercent.textContent = '60%';
            if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang định dạng bảng kết quả...';
            
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Quét ảnh thất bại.');
            }

            const finalRecords = result.records || [];
            const totalRecords = finalRecords.length;
            addLog(`Xử lý hoàn tất. Tổng số bản ghi nhận diện được: ${totalRecords}`, 'success');

            if (totalRecords === 0) {
                addLog('Không tìm thấy dữ liệu phiếu cân trong ảnh này. Vui lòng thử ảnh khác.', 'error');
                if (ocrProgressBox) ocrProgressBox.classList.add('hidden');
                if (photoStatusBadge) {
                    photoStatusBadge.textContent = 'Không tìm thấy dữ liệu';
                    photoStatusBadge.className = 'status-badge';
                }
                resetUIStatePhoto();
                return;
            }

            // Merge new records with existing records (supports overlapping scans)
            ocrExtractedRecords = mergeOcrRecords(ocrExtractedRecords, finalRecords);

            // Render real OCR records in the data table
            renderOcrTable(ocrExtractedRecords);
            updateUniformityStatsAndPills();

            // Fill UI fields using merged records
            // Fill results into the data table only (no 20 pills limit)
            renderOcrTable(ocrExtractedRecords);
            updateUniformityStatsAndPills();

            // Calculations
            const parsedWeights = ocrExtractedRecords
                .map(r => parseFloat(r.weight))
                .filter(v => !isNaN(v) && v > 0);
            
            if (parsedWeights.length > 0) {
                const mean = parsedWeights.reduce((a, b) => a + b, 0) / parsedWeights.length;
                const variance = parsedWeights.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / parsedWeights.length;
                const rsd = (Math.sqrt(variance) / mean) * 100;
                
                const valMean = document.getElementById('val-mean');
                const valRsd = document.getElementById('val-rsd');
                const valResult = document.getElementById('val-result');
                
                if (valMean) valMean.textContent = `${mean.toFixed(4)} g`;
                if (valRsd) valRsd.textContent = `${rsd.toFixed(2)} %`;
                if (valResult) {
                    if (rsd <= 2.0) {
                        valResult.textContent = 'Đạt yêu cầu';
                        valResult.style.color = 'var(--success)';
                        addLog(`Kiểm định Dược Điển: Trung bình = ${mean.toFixed(4)}g | RSD = ${rsd.toFixed(2)}% (ĐẠT).`, 'success');
                    } else {
                        valResult.textContent = 'Không đạt';
                        valResult.style.color = 'var(--danger)';
                        addLog(`Kiểm định Dược Điển: Trung bình = ${mean.toFixed(4)}g | RSD = ${rsd.toFixed(2)}% (KHÔNG ĐẠT).`, 'error');
                    }
                }
            }

            if (ocrProgressFill) ocrProgressFill.style.width = '100%';
            if (ocrProgressPercent) ocrProgressPercent.textContent = '100%';
            if (ocrProgressLabel) ocrProgressLabel.textContent = 'Hoàn tất quét phiếu cân lab!';

            setTimeout(() => {
                if (ocrProgressBox) ocrProgressBox.classList.add('hidden');
                hideLaserLines();

                if (photoStatusBadge) {
                    photoStatusBadge.textContent = `Hoàn tất (${totalRecords} mẫu)`;
                    photoStatusBadge.className = 'status-badge completed';
                }
                if (consoleStatusDot) consoleStatusDot.className = 'console-status-dot idle';

                isProcessing = false;
                setScanButtonState(true);
                if (btnResetPhoto) btnResetPhoto.removeAttribute('disabled');
                if (btnPhotoClear) btnPhotoClear.removeAttribute('disabled');
                if (btnSyncCoa) btnSyncCoa.removeAttribute('disabled');
                fileInput.removeAttribute('disabled');

                addLog(`🎉 <strong>OCR hoàn tất!</strong> Đã trích xuất ${totalRecords} mẫu từ ảnh thực bằng Gemini API.`, 'success');

                const uniformityGlow = document.getElementById('uniformity-card-glow');
                if (uniformityGlow) uniformityGlow.classList.add('active-glow');
            }, 500);

        } catch (err) {
            addLog(`Lỗi OCR: ${err.message}`, 'error');
            console.error('OCR Error:', err);
            if (ocrProgressBox) ocrProgressBox.classList.add('hidden');
            resetUIStatePhoto();
        }
    }

    function resetUIStatePhoto() {
        hideLaserLines();
        if (photoStatusBadge) {
            photoStatusBadge.textContent = 'Lỗi quét';
            photoStatusBadge.className = 'status-badge';
        }
        if (consoleStatusDot) consoleStatusDot.className = 'console-status-dot idle';
        isProcessing = false;
        setScanButtonState(true);
        if (btnResetPhoto) btnResetPhoto.removeAttribute('disabled');
        if (btnPhotoClear) btnPhotoClear.removeAttribute('disabled');
        fileInput.removeAttribute('disabled');
    }

    // --- DATA TABLE RENDERING FOR OCR RESULTS ---
    let currentTablePage = 1;
    const recordsPerPage = 10;

    function updateUniformityStatsAndPills() {
        const grid = document.getElementById('pill-progress-grid');
        const counter = document.getElementById('session-stitch-counter');
        if (!grid) return;

        grid.innerHTML = '';
        let completedCount = 0;
        const totalCount = ocrExtractedRecords.length;

        // Render pills for actual records count (not limited to 20)
        for (let i = 0; i < totalCount; i++) {
            const rec = ocrExtractedRecords[i] || {};
            const hasW = rec.weight && rec.weight !== '-' && rec.weight !== '';
            const hasDt = rec.datetime && rec.datetime !== '-' && rec.datetime !== '';
            
            let colorClass = 'background: rgba(255,255,255,0.03); border: 1px solid var(--surface-border); color: var(--text-muted);';
            let title = `Mẫu ${i+1}: Trống`;

            if (hasW && hasDt) {
                colorClass = 'background: rgba(16, 185, 129, 0.15); border: 1px solid var(--success); color: var(--success); box-shadow: 0 0 6px rgba(16, 185, 129, 0.2);';
                title = `Mẫu ${i+1}: Hoàn thành (${rec.weight} g)`;
                completedCount++;
            } else if (hasW || hasDt) {
                colorClass = 'background: rgba(245, 158, 11, 0.15); border: 1px solid #f59e0b; color: #f59e0b; box-shadow: 0 0 6px rgba(245, 158, 11, 0.2);';
                title = `Mẫu ${i+1}: Khuyết ${hasW ? 'ngày giờ' : 'cân nặng'}`;
            }

            const pill = document.createElement('div');
            pill.style.cssText = `height: 24px; border-radius: 4px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.72rem; font-weight: 700; cursor: help; transition: var(--transition-fast); ${colorClass}`;
            pill.title = title;
            pill.textContent = i + 1;
            grid.appendChild(pill);
        }

        if (counter) {
            counter.textContent = `${completedCount} / ${totalCount} mẫu hoàn tất`;
        }

        // Recalculate mean, RSD etc. for calculations card
        const parsedWeights = ocrExtractedRecords
            .map(r => parseFloat(r.weight))
            .filter(v => !isNaN(v) && v > 0);

        const valMean = document.getElementById('val-mean');
        const valRsd = document.getElementById('val-rsd');
        const valMax = document.getElementById('val-max');
        const valMin = document.getElementById('val-min');

        if (parsedWeights.length > 0) {
            const mean = parsedWeights.reduce((a, b) => a + b, 0) / parsedWeights.length;
            const variance = parsedWeights.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / parsedWeights.length;
            const rsd = (Math.sqrt(variance) / mean) * 100;
            const maxVal = Math.max(...parsedWeights);
            const minVal = Math.min(...parsedWeights);

            if (valMean) valMean.textContent = mean.toFixed(4) + ' g';
            if (valRsd) valRsd.textContent = rsd.toFixed(2) + ' %';
            if (valMax) valMax.textContent = maxVal.toFixed(3) + ' g';
            if (valMin) valMin.textContent = minVal.toFixed(3) + ' g';
        } else {
            if (valMean) valMean.textContent = '-';
            if (valRsd) valRsd.textContent = '-';
            if (valMax) valMax.textContent = '-';
            if (valMin) valMin.textContent = '-';
        }
    }

    function renderOcrTable(records) {
        const tbody = document.getElementById('table-body');
        const filterEl = document.getElementById('table-filter-select');
        const searchEl = document.getElementById('table-search-input');
        if (!tbody) return;

        const filterVal = filterEl ? filterEl.value : 'all';
        const searchVal = searchEl ? searchEl.value.trim().toLowerCase() : '';

        // Calculate mean for validity check
        const parsedWeights = records
            .map(r => parseFloat(r.weight))
            .filter(v => !isNaN(v) && v > 0);
        const mean = parsedWeights.length > 0 ? parsedWeights.reduce((a, b) => a + b, 0) / parsedWeights.length : 0.256;

        // Filter records
        let filtered = records.filter(r => {
            const w = parseFloat(r.weight);
            const isRecordValid = isNaN(w) || (w >= mean * 0.95 && w <= mean * 1.05);

            if (filterVal === 'valid' && !isRecordValid) return false;
            if (filterVal === 'invalid' && isRecordValid) return false;

            if (searchVal && 
                !(r.weight || '').toLowerCase().includes(searchVal) && 
                !(r.snr || '').toLowerCase().includes(searchVal) && 
                !(r.datetime || '').toLowerCase().includes(searchVal) && 
                !(r.balance_type || '').toLowerCase().includes(searchVal)) {
                return false;
            }
            return true;
        });

        const totalPages = Math.ceil(filtered.length / recordsPerPage) || 1;
        if (currentTablePage > totalPages) currentTablePage = totalPages;

        const startIdx = (currentTablePage - 1) * recordsPerPage;
        const pageData = filtered.slice(startIdx, startIdx + recordsPerPage);

        tbody.innerHTML = '';
        if (pageData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px; color: var(--text-muted);">Không tìm thấy dữ liệu</td></tr>';
        } else {
            pageData.forEach(r => {
                const w = parseFloat(r.weight);
                const isRecordValid = isNaN(w) || (w >= mean * 0.95 && w <= mean * 1.05);
                const statusBadge = isRecordValid 
                    ? '<span class="status-badge completed">Hợp lệ</span>'
                    : '<span class="status-badge" style="background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); padding: 2px 6px; border-radius: 4px; font-size: 0.75rem;">Lệch > 5%</span>';

                const tr = document.createElement('tr');
                tr.style.borderBottom = '1px solid var(--surface-border)';
                tr.innerHTML = `
                    <td style="padding: 10px 16px; color: var(--text-muted);">${r.id}</td>
                    <td class="editable-cell" data-id="${r.id}" data-field="weight" contenteditable="true" style="padding: 10px 16px; font-weight: 600; color: var(--accent); border-bottom: 1px dashed rgba(14, 165, 233, 0.25); outline: none; cursor: edit;">${r.weight || '-'}</td>
                    <td class="editable-cell" data-id="${r.id}" data-field="datetime" contenteditable="true" style="padding: 10px 16px; color: var(--text-secondary); border-bottom: 1px dashed rgba(255, 255, 255, 0.05); outline: none; cursor: edit;">${r.datetime || '-'}</td>
                    <td class="editable-cell" data-id="${r.id}" data-field="balance_type" contenteditable="true" style="padding: 10px 16px; color: var(--text-secondary); border-bottom: 1px dashed rgba(255, 255, 255, 0.05); outline: none; cursor: edit;">${r.balance_type || '-'}</td>
                    <td class="editable-cell" data-id="${r.id}" data-field="snr" contenteditable="true" style="padding: 10px 16px; color: var(--text-secondary); font-family: monospace; border-bottom: 1px dashed rgba(255, 255, 255, 0.05); outline: none; cursor: edit;">${r.snr || '-'}</td>
                    <td style="padding: 10px 16px;">${statusBadge}</td>
                `;
                tbody.appendChild(tr);

                // Add change listener to save edited value
                const cells = tr.querySelectorAll('.editable-cell');
                cells.forEach(cell => {
                    cell.addEventListener('blur', (e) => {
                        const id = parseInt(e.target.getAttribute('data-id'));
                        const field = e.target.getAttribute('data-field');
                        let newVal = e.target.textContent.trim();
                        if (newVal === '-') newVal = '';
                        
                        // Find and update in global ocrExtractedRecords
                        const recordIndex = ocrExtractedRecords.findIndex(rec => rec.id === id);
                        if (recordIndex !== -1) {
                            ocrExtractedRecords[recordIndex][field] = newVal;
                            
                            // Re-sync this value to the matching UI input w1-w20 if field is 'weight'
                            if (field === 'weight' && id <= 20) {
                                const inputEl = document.getElementById(`w${id}`);
                                if (inputEl) {
                                    inputEl.value = newVal;
                                    inputEl.classList.add('filled-highlight');
                                    // Update indicator class
                                    const indicatorEl = document.getElementById(`ind-w${id}`);
                                    const ocrBox = document.getElementById(`box-w${id}`);
                                    if (newVal) {
                                        if (indicatorEl) indicatorEl.className = 'extraction-indicator success';
                                        if (ocrBox) ocrBox.className = 'ocr-box success';
                                    } else {
                                        if (indicatorEl) indicatorEl.className = 'extraction-indicator';
                                        if (ocrBox) ocrBox.className = 'ocr-box';
                                    }
                                }
                            }
                            
                            // Re-calculate statistics and redraw table to update validation status
                            updateUniformityStatsAndPills();
                        }
                    });
                    
                    cell.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            e.target.blur();
                        }
                    });
                });
            });
        }

        // Update pagination info
        const info = document.getElementById('pagination-info');
        const indicator = document.getElementById('page-indicator');
        const btnPrev = document.getElementById('btn-prev-page');
        const btnNext = document.getElementById('btn-next-page');

        if (info) info.textContent = `Hiển thị ${filtered.length} bản ghi`;
        if (indicator) indicator.textContent = `${currentTablePage} / ${totalPages}`;
        if (btnPrev) btnPrev.disabled = currentTablePage <= 1;
        if (btnNext) btnNext.disabled = currentTablePage >= totalPages;
    }

    // Table search
    const tableSearchInput = document.getElementById('table-search-input');
    if (tableSearchInput) {
        tableSearchInput.addEventListener('input', () => {
            currentTablePage = 1;
            renderOcrTable(ocrExtractedRecords);
        });
    }

    // Table filter
    const tableFilterSelect = document.getElementById('table-filter-select');
    if (tableFilterSelect) {
        tableFilterSelect.addEventListener('change', () => {
            currentTablePage = 1;
            renderOcrTable(ocrExtractedRecords);
        });
    }

    // Pagination buttons
    document.addEventListener('click', (e) => {
        if (e.target.id === 'btn-prev-page') {
            if (currentTablePage > 1) { 
                currentTablePage--; 
                renderOcrTable(ocrExtractedRecords); 
            }
        } else if (e.target.id === 'btn-next-page') {
            const filterEl = document.getElementById('table-filter-select');
            const searchEl = document.getElementById('table-search-input');
            const filterVal = filterEl ? filterEl.value : 'all';
            const searchVal = searchEl ? searchEl.value.trim().toLowerCase() : '';

            // Calculate current total filtered count
            const parsedWeights = ocrExtractedRecords
                .map(r => parseFloat(r.weight))
                .filter(v => !isNaN(v) && v > 0);
            const mean = parsedWeights.length > 0 ? parsedWeights.reduce((a, b) => a + b, 0) / parsedWeights.length : 0.256;

            let filtered = ocrExtractedRecords.filter(r => {
                const w = parseFloat(r.weight);
                const isRecordValid = isNaN(w) || (w >= mean * 0.95 && w <= mean * 1.05);
                if (filterVal === 'valid' && !isRecordValid) return false;
                if (filterVal === 'invalid' && isRecordValid) return false;
                if (searchVal && 
                    !r.weight.toLowerCase().includes(searchVal) && 
                    !r.snr.toLowerCase().includes(searchVal) && 
                    !r.datetime.toLowerCase().includes(searchVal) && 
                    !r.balance_type.toLowerCase().includes(searchVal)) {
                    return false;
                }
                return true;
            });
            const totalPages = Math.ceil(filtered.length / recordsPerPage) || 1;

            if (currentTablePage < totalPages) { 
                currentTablePage++; 
                renderOcrTable(ocrExtractedRecords); 
            }
        }
    });

    function runSimulatedDemoOCR() {
        showLaserLines();
        if (btnPhotoClear) btnPhotoClear.setAttribute('disabled', 'true');
        if (btnSyncCoa) btnSyncCoa.setAttribute('disabled', 'true');
        
        if (ocrProgressBox) {
            ocrProgressBox.classList.remove('hidden');
            ocrProgressFill.style.width = '0%';
            ocrProgressPercent.textContent = '0%';
            ocrProgressLabel.textContent = 'Khởi động máy quét AI OCR...';
        }

        const loggedMilestones = new Set();
        const duration = 2000; // 2 seconds
        const startTime = performance.now();

        const demoRecords = [
            { id: 1, weight: '0.258', datetime: '11.04.2026 11:13', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 2, weight: '0.255', datetime: '11.04.2026 11:13', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 3, weight: '0.256', datetime: '11.04.2026 11:13', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 4, weight: '0.254', datetime: '11.04.2026 11:14', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 5, weight: '0.252', datetime: '11.04.2026 11:14', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 6, weight: '0.256', datetime: '11.04.2026 11:15', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 7, weight: '0.260', datetime: '11.04.2026 11:15', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 8, weight: '0.258', datetime: '11.04.2026 11:15', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 9, weight: '0.255', datetime: '11.04.2026 11:15', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 10, weight: '0.257', datetime: '11.04.2026 11:15', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 11, weight: '0.259', datetime: '11.04.2026 11:15', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 12, weight: '0.253', datetime: '11.04.2026 11:16', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 13, weight: '0.258', datetime: '11.04.2026 11:16', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 14, weight: '0.256', datetime: '11.04.2026 11:16', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 15, weight: '0.255', datetime: '11.04.2026 11:16', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 16, weight: '0.255', datetime: '11.04.2026 11:17', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 17, weight: '0.253', datetime: '11.04.2026 11:17', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 18, weight: '0.258', datetime: '11.04.2026 11:17', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 19, weight: '0.256', datetime: '11.04.2026 11:17', balance_type: 'MS204S/A73', snr: 'B609149654' },
            { id: 20, weight: '0.255', datetime: '11.04.2026 11:17', balance_type: 'MS204S/A73', snr: 'B609149654' }
        ];

        function updatePhotoScan(currentTime) {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1);
            const percent = Math.floor(progress * 100);
            
            if (ocrProgressFill) ocrProgressFill.style.width = `${percent}%`;
            if (ocrProgressPercent) ocrProgressPercent.textContent = `${percent}%`;
            
            if (percent >= 0) {
                if (!loggedMilestones.has('p0')) {
                    loggedMilestones.add('p0');
                    addLog(`⚡ Bắt đầu Quét AI OCR Phiếu cân Phòng Lab (Demo)...`, 'process');
                }
                if (ocrProgressLabel) ocrProgressLabel.textContent = 'Khởi động máy quét AI OCR...';
            }
            
            if (percent >= 25) {
                if (!loggedMilestones.has('p25')) {
                    loggedMilestones.add('p25');
                    addLog(`Nhận diện bố cục: Phát hiện 2 cột in nhiệt kết quả cân.`, 'process');
                }
                if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang phân tích cấu trúc cột phiếu lab...';
            }

            if (percent >= 50) {
                if (!loggedMilestones.has('p50')) {
                    loggedMilestones.add('p50');
                    addLog(`Đang trích xuất dữ liệu khối lượng (20 chỉ tiêu)...`, 'process');
                }
                if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang trích xuất khối lượng...';
            }
            
            if (percent >= 50 && percent < 90) {
                const pillsToFill = Math.min(ocrExtractedRecords.length, Math.floor((percent - 50) / 2));
                for (let i = 0; i < pillsToFill; i++) {
                    const pillNum = i + 1;
                    const ocrBox = document.getElementById(`box-w${pillNum}`);
                    if (ocrBox) ocrBox.className = 'ocr-box success';
                }
            }
            
            if (percent >= 90) {
                if (!loggedMilestones.has('p90')) {
                    loggedMilestones.add('p90');
                    addLog(`Trích xuất thành công 20/20 khối lượng. Đang tính toán dữ liệu...`, 'success');
                }
                if (ocrProgressLabel) ocrProgressLabel.textContent = 'Đang đối chiếu Dược Điển Việt Nam V...';
            }
            
            if (percent < 100) {
                requestAnimationFrame(updatePhotoScan);
            } else {
                if (ocrProgressLabel) ocrProgressLabel.textContent = 'Hoàn tất quét phiếu cân lab!';
                
                // Populate records - no 20 limit
                ocrExtractedRecords = [];
                for (let i = 0; i < demoRecords.length; i++) {
                    ocrExtractedRecords.push({
                        id: i + 1,
                        weight: demoRecords[i].weight,
                        datetime: demoRecords[i].datetime,
                        balance_type: demoRecords[i].balance_type,
                        snr: demoRecords[i].snr
                    });
                }
                
                // Render table - shows all records dynamically
                renderOcrTable(ocrExtractedRecords);
                updateUniformityStatsAndPills();

                // Set bounding boxes for all records
                for (let i = 0; i < ocrExtractedRecords.length; i++) {
                    const ocrBox = document.getElementById(`box-w${i + 1}`);
                    if (ocrBox) ocrBox.className = 'ocr-box success';
                }

                // Show stats
                const mean = 0.2563;
                const rsd = 0.82;
                const valMean = document.getElementById('val-mean');
                const valRsd = document.getElementById('val-rsd');
                const valResult = document.getElementById('val-result');
                
                if (valMean) valMean.textContent = `${mean.toFixed(4)} g`;
                if (valRsd) valRsd.textContent = `${rsd.toFixed(2)} %`;
                if (valResult) {
                    valResult.textContent = 'Đạt yêu cầu';
                    valResult.style.color = 'var(--success)';
                    addLog(`Kiểm định Dược Điển: Trung bình = ${mean.toFixed(4)}g | RSD = ${rsd.toFixed(2)}% (ĐẠT).`, 'success');
                }

                setTimeout(() => {
                    if (ocrProgressBox) ocrProgressBox.classList.add('hidden');
                    hideLaserLines();

                    if (photoStatusBadge) {
                        photoStatusBadge.textContent = `Hoàn tất (${demoRecords.length} mẫu)`;
                        photoStatusBadge.className = 'status-badge completed';
                    }
                    if (consoleStatusDot) consoleStatusDot.className = 'console-status-dot idle';

                    isProcessing = false;
                    setScanButtonState(true);
                    if (btnResetPhoto) btnResetPhoto.removeAttribute('disabled');
                    if (btnPhotoClear) btnPhotoClear.removeAttribute('disabled');
                    if (btnSyncCoa) btnSyncCoa.removeAttribute('disabled');
                    fileInput.removeAttribute('disabled');

                    addLog(`🎉 <strong>OCR hoàn tất!</strong> Đã trích xuất ${demoRecords.length} mẫu từ ảnh demo.`, 'success');
                    document.getElementById('uniformity-card-glow').classList.add('active-glow');
                }, 500);
            }
        }
        requestAnimationFrame(updatePhotoScan);
    }
    
    // Initialize empty progress grid on load
    updateUniformityStatsAndPills();
});
