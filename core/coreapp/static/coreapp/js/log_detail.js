 document.addEventListener('DOMContentLoaded', function() {
    const hWheel = document.getElementById('modalHourWheel');
    const mWheel = document.getElementById('modalMinuteWheel');
    let isGlobalDragging = false;

    // Sử dụng Intersection Observer để nhận diện số nằm giữa wheel (Cực mượt, không ăn CPU)
    function createWheelObserver(wheelNode) {
        const options = {
            root: wheelNode,
            rootMargin: '-40px 0px -40px 0px', // Thu hẹp vùng ngắm vào đúng giữa thanh tiêu điểm (cao ~30px)
            threshold: 0.6
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Xóa active cũ trong cùng wheel
                    wheelNode.querySelectorAll('.wheel-number').forEach(el => el.classList.remove('active-ios'));
                    // Thêm active cho thằng nằm giữa
                    entry.target.classList.add('active-ios');
                }
            });
        }, options);

        return observer;
    }

    // Vuốt kéo bằng chuột mượt mà trên PC
    function enableMouseDragScroll(wheelNode) {
        let isDown = false;
        let startY, scrollTop;

        wheelNode.addEventListener('mousedown', (e) => {
            isDown = true;
            isGlobalDragging = false;
            wheelNode.style.scrollSnapType = 'none'; // Tạm tắt snap khi đang kéo tay để tránh giật
            startY = e.pageY - wheelNode.offsetTop;
            scrollTop = wheelNode.scrollTop;
        });

        wheelNode.addEventListener('mouseleave', () => { 
            if (isDown) { isDown = false; wheelNode.style.scrollSnapType = 'y mandatory'; }
        });

        wheelNode.addEventListener('mouseup', () => { 
            if (isDown) { isDown = false; wheelNode.style.scrollSnapType = 'y mandatory'; }
        });

        wheelNode.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            isGlobalDragging = true;
            const y = e.pageY - wheelNode.offsetTop;
            const walk = (y - startY) * 1.5; // Tốc độ cuộn chuột
            wheelNode.scrollTop = scrollTop - walk;
        });
    }

    function generateWheelNumbers(wheelNode, totalCount) {
        const spacerEnd = wheelNode.lastElementChild;
        const observer = createWheelObserver(wheelNode);

        for (let i = 0; i < totalCount; i++) {
            const numDiv = document.createElement('div');
            numDiv.className = 'wheel-number';
            numDiv.style.cursor = 'pointer';
            numDiv.style.userSelect = 'none';
            numDiv.textContent = i.toString().padStart(2, '0');
            
            // Mở nhanh chế độ nhập tay khi click
            numDiv.addEventListener('click', function(e) {
                if (isGlobalDragging) return; 
                e.stopPropagation();
                openManualInput(numDiv, wheelNode, totalCount);
            });

            wheelNode.insertBefore(numDiv, spacerEnd);
            observer.observe(numDiv); // Kích hoạt theo dõi số này
        }

        // Kích hoạt kéo chuột trên PC, Mobile xài scroll native đã có scroll-snap lo
        enableMouseDragScroll(wheelNode);
    }

    function openManualInput(targetNode, wheelNode, maxLimit) {
        if (targetNode.querySelector('input')) return;
        const currentVal = targetNode.textContent;
        targetNode.textContent = '';

        const inputEl = document.createElement('input');
        inputEl.type = 'number'; inputEl.min = 0; inputEl.max = maxLimit - 1; inputEl.value = parseInt(currentVal);
        inputEl.style.width = '45px'; inputEl.style.height = '24px'; inputEl.style.background = '#fe2c55';
        inputEl.style.color = '#ffffff'; inputEl.style.border = 'none'; inputEl.style.borderRadius = '4px';
        inputEl.style.textAlign = 'center'; inputEl.style.fontSize = '1rem'; inputEl.style.fontWeight = 'bold'; inputEl.style.outline = 'none';

        function saveManualValue() {
            let inputNum = parseInt(inputEl.value) || 0;
            if (inputNum < 0) inputNum = 0;
            if (inputNum >= maxLimit) inputNum = maxLimit - 1;
            const finalStr = inputNum.toString().padStart(2, '0');
            targetNode.textContent = finalStr;

            const allNodes = Array.from(wheelNode.querySelectorAll('.wheel-number'));
            const targetIndex = allNodes.findIndex(node => node.textContent === finalStr);
            if (targetIndex !== -1) {
                wheelNode.scrollTo({ top: targetIndex * 30, behavior: 'smooth' });
            }
        }

        inputEl.addEventListener('blur', saveManualValue);
        inputEl.addEventListener('keydown', function(e) { if (e.key === 'Enter') { e.preventDefault(); saveManualValue(); } });
        targetNode.appendChild(inputEl); inputEl.focus(); inputEl.select(); 
    }

    // Khởi tạo 2 cột số
    generateWheelNumbers(hWheel, 24);
    generateWheelNumbers(mWheel, 60);

    // Reset vị trí cuộn về 00:00 mỗi khi mở Modal để tránh lỗi hiển thị lệch
    document.getElementById('iphoneTimePickerModal').addEventListener('shown.bs.modal', () => {
        hWheel.scrollTop = 0;
        mWheel.scrollTop = 0;
    });

    // ================= XỬ LÝ SEARCH TEXT GỐC =================
    const searchInput = document.getElementById('logSearchInput');
    const searchBtn = document.getElementById('logSearchBtn');

    function runTextSearch() {
        const textQuery = searchInput.value.trim().toLowerCase();
        if (!textQuery) return;

        resetAllHighlights();
        const items = document.querySelectorAll('.js-timeline-node');
        let targetMatch = null;

        for (let item of items) {
            const userAttr = item.getAttribute('data-search-username') || '';
            const phoneAttr = item.getAttribute('data-search-phone') || '';
            if (userAttr.includes(textQuery) || phoneAttr.includes(textQuery)) {
                targetMatch = item; break;
            }
        }
        applyFocusAndHighlight(targetMatch);
    }

    searchBtn.addEventListener('click', runTextSearch);
    searchInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); runTextSearch(); } });

    // ================= CHỌN GIỜ TRÊN MODAL VÀ NHẢY TIMELINE =================
    const modalSubmitBtn = document.getElementById('modalTimeSubmitBtn');
    modalSubmitBtn.addEventListener('click', function() {
        const pickedHour = hWheel.querySelector('.wheel-number.active-ios')?.textContent || "00";
        const pickedMinute = mWheel.querySelector('.wheel-number.active-ios')?.textContent || "00";
        const finalTimeQuery = `${pickedHour}:${pickedMinute}`;

        resetAllHighlights();
        const items = document.querySelectorAll('.js-timeline-node');
        let matchPerfect = null, matchBackupHour = null;

        for (let item of items) {
            const timeAttr = item.getAttribute('data-search-time') || '';
            if (timeAttr === finalTimeQuery) { matchPerfect = item; break; }
            if (!matchBackupHour && timeAttr.startsWith(pickedHour + ':')) { matchBackupHour = item; }
        }

        const chosenNode = matchPerfect || matchBackupHour;
        if (chosenNode) {
            const currentModal = bootstrap.Modal.getInstance(document.getElementById('iphoneTimePickerModal'));
            if (currentModal) currentModal.hide();
            setTimeout(() => { applyFocusAndHighlight(chosenNode); }, 300);
        } else {
            alert(`Không tìm thấy nhật ký nào trong khung giờ ${finalTimeQuery}!`);
        }
    });

    function resetAllHighlights() {
        document.querySelectorAll('.js-timeline-node').forEach(node => { node.classList.remove('highlight-match'); });
    }

    function applyFocusAndHighlight(node) {
        if (node) {
            node.scrollIntoView({ behavior: 'smooth', block: 'center' });
            node.classList.add('highlight-match');
            setTimeout(() => { node.classList.remove('highlight-match'); }, 3600);
        } else {
            alert('Không tìm thấy bản ghi phù hợp!');
        }
    }
});
