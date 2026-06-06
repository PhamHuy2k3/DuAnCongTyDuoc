document.addEventListener('DOMContentLoaded', function () {
    // 1. Logic chuyển tab
    const tabButtons = document.querySelectorAll('.db-menu-item');
    const tabPanes = document.querySelectorAll('.db-tab-pane');
    const tabTitle = document.getElementById('db-tab-title');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.add('hidden'));

            button.classList.add('active');
            const targetTabId = button.getAttribute('data-tab');
            const targetPane = document.getElementById(targetTabId);
            if (targetPane) targetPane.classList.remove('hidden');

            if (tabTitle) {
                tabTitle.textContent = button.querySelector('span').textContent;
            }
        });
    });
});

// === LOGIC ĐIỀU KHIỂN MODAL RESET MẬT KHẨU ===
function openResetModal(username) {
    const modal = document.getElementById('reset-modal');
    if (!modal) return;
    
    document.getElementById('reset-target-user').innerText = username;
    document.getElementById('reset-hidden-user').value = username;
    
    // Placeholder thông minh
    const randomSuffix = Math.random().toString(36).slice(-4).toUpperCase();
    modal.querySelector('input[name="new_password"]').placeholder = `Ví dụ: Pwd@${randomSuffix}`;
    
    modal.classList.remove('hidden');
}

// === LOGIC ĐIỀU KHIỂN MODAL KHÓA & MỞ TÀI KHOẢN ===
function openLockModal(username, actionState) {
    const modal = document.getElementById('lock-modal');
    const title = document.getElementById('lock-modal-title');
    const desc = document.getElementById('lock-modal-desc');
    const submitBtn = document.getElementById('lock-modal-submit-btn');

    if (!modal) return;

    document.getElementById('lock-hidden-user').value = username;
    document.getElementById('lock-hidden-status').value = actionState;

    if (actionState === 'lock') {
        title.innerHTML = "🔒 Đình chỉ tài khoản nhân sự";
        desc.innerHTML = `Xác nhận **KHÓA** tài khoản <strong style="color:#ef4444;">${username}</strong>? Họ sẽ mất quyền truy cập hệ thống.`;
        submitBtn.innerText = "Xác nhận Khóa";
        submitBtn.style.backgroundColor = "#ef4444";
    } else {
        title.innerHTML = "🔓 Kích hoạt lại tài khoản";
        desc.innerHTML = `Xác nhận khôi phục quyền làm việc cho tài khoản <strong style="color:#10b981;">${username}</strong>?`;
        submitBtn.innerText = "Mở khóa tài khoản";
        submitBtn.style.backgroundColor = "#10b981";
    }

    modal.classList.remove('hidden');
}

// === HÀM TIỆN ÍCH DÙNG CHUNG ===
function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

// Hàm copy dùng cho mật khẩu (Sử dụng trực tiếp giá trị text)
function copyToClipboard(text, btnElement) {
    // 1. CHẶN COPY: Nếu là thông báo "Người dùng đã đổi mật khẩu" hoặc dữ liệu trống
    if (!text || text === "---" || text === "Người dùng đã đổi mật khẩu") {
        console.log("Không thể copy thông báo hệ thống.");
        return;
    }
    
    // 2. Thực hiện copy bình thường
    navigator.clipboard.writeText(text).then(() => {
        const originalHTML = btnElement.innerHTML;
        
        btnElement.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
        btnElement.classList.add('copied');
        
        setTimeout(() => {
            btnElement.innerHTML = originalHTML;
            btnElement.classList.remove('copied');
        }, 1500);
    }).catch(err => {
        console.error('Lỗi khi copy: ', err);
    });
}

function toggleCreateForm() {
    const formCard = document.getElementById('create-user-form-card');
    if (formCard) formCard.classList.toggle('hidden');
}

function openDeleteModal(username) {
    const tokenEl = document.getElementById('csrf-token');
    if (!tokenEl) {
        alert("Lỗi hệ thống: Không tìm thấy CSRF Token!");
        return;
    }

    if (confirm("Bạn có chắc chắn muốn xóa tài khoản " + username + "?")) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '';
        form.innerHTML = `
            <input type="hidden" name="csrfmiddlewaretoken" value="${tokenEl.value}">
            <input type="hidden" name="action_type" value="delete_user">
            <input type="hidden" name="target_username" value="${username}">
        `;
        document.body.appendChild(form);
        form.submit();
    }
}

function openViewModal(btn) {
    const modal = document.getElementById('view-modal');
    if (!modal) return;
    
    // Gán dữ liệu cơ bản
    document.getElementById('v-username').innerText = btn.getAttribute('data-username') || '---';
    document.getElementById('v-email').innerText = btn.getAttribute('data-email') || '---';
    document.getElementById('v-fullname').innerText = btn.getAttribute('data-fullname') || '---';
    document.getElementById('v-role').innerText = btn.getAttribute('data-role') || '---';
    document.getElementById('v-birth').innerText = btn.getAttribute('data-birth') || '---';
    document.getElementById('v-phone').innerText = btn.getAttribute('data-phone') || '---';
    
    // XỬ LÝ MẬT KHẨU
    const passwordSpan = document.getElementById('v-password');
    const copyBtn = document.getElementById('v-copy-btn');
    
    // Kiểm tra giá trị từ HTML (hỗ trợ cả True/true)
    const attrChanged = btn.getAttribute('data-password-changed');
    const isChanged = (attrChanged === 'True' || attrChanged === 'true');
    const passwordVal = btn.getAttribute('data-password');
    
    if (isChanged) {
        passwordSpan.innerText = "Người dùng đã đổi mật khẩu";
        passwordSpan.style.color = "#64748b";
        passwordSpan.style.fontStyle = "italic";
        copyBtn.style.display = 'none'; // ẨN NÚT COPY
    } else {
        passwordSpan.innerText = passwordVal || '---';
        passwordSpan.style.color = "#48bb78";
        passwordSpan.style.fontStyle = "normal";
        copyBtn.style.display = 'inline-flex'; // HIỆN NÚT COPY
    }
    
    // Xử lý Trạng thái
    const statusSpan = document.getElementById('v-status');
    const attrActive = btn.getAttribute('data-active');
    const isActive = (attrActive === 'True' || attrActive === 'true');
    statusSpan.innerText = isActive ? "Đang hoạt động" : "Đang khóa";
    statusSpan.style.color = isActive ? "#10b981" : "#ef4444";
    
    modal.classList.remove('hidden');
}

document.addEventListener('DOMContentLoaded', function () {
    // Sử dụng sự kiện "Ủy quyền" (Event Delegation) trên body
    document.body.addEventListener('click', function (e) {
        // Kiểm tra nếu phần tử bị click là nút Xóa (hoặc con của nó)
        const deleteBtn = e.target.closest('.js-delete');
        
        if (deleteBtn) {
            const username = deleteBtn.getAttribute('data-username');
            // Gọi lại hàm xóa cũ của bạn
            openDeleteModal(username);
        }
    });
});

function toggleSidebar() {
    const sidebar = document.querySelector('.db-sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
}

// Tự động đóng khi nhấn vào mục menu
document.querySelectorAll('.db-menu-item').forEach(item => {
    item.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
            toggleSidebar();
        }
    });
});
// Đóng modal khi click ra ngoài overlay
window.onclick = function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.classList.add('hidden');
    }
}

