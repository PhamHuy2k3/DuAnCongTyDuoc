
    let audioContext, animationId, stream, recognition;
    let isManuallyStopped = false;

window.stopSiriManually = function() {
    if (recognition) {
        isManuallyStopped = true;
        
        // 1. Ẩn giao diện NGAY LẬP TỨC
        const orbContainer = document.getElementById('siri-orb-container');
        const micBtn = document.getElementById('btn-mic');
        orbContainer.classList.add('hidden');
        micBtn.classList.remove('hidden');
        
        // 2. Dừng ghi âm
        recognition.stop(); 
        console.log("Đã dừng Siri thủ công");
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // Thêm đoạn này vào bên trong document.addEventListener('DOMContentLoaded', ...)
    const clearBtn = document.getElementById('clear-search');
    const micBtn = document.getElementById('btn-mic');
    const orbContainer = document.getElementById('siri-orb-container');
    const searchForm = document.getElementById('main-search-form');
    const searchInput = document.querySelector('input[name="q"]');
    
    clearBtn.addEventListener('click', () => {
        searchInput.value = ""; // Xóa text
        
        // Hiện lại nút Mic, ẩn quả cầu
        micBtn.classList.remove('hidden');
        orbContainer.classList.add('hidden');
        
        // Tự động load lại trang về trạng thái không filter
        window.location.href = window.location.pathname; 
    });
    function toggleMic(isRecording) {
        if (isRecording) {
            micBtn.classList.add('hidden');
            orbContainer.classList.remove('hidden');
        } else {
            orbContainer.classList.add('hidden');
            micBtn.classList.remove('hidden');
        }
    }

    async function startAudio() {
        try {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const analyser = audioContext.createAnalyser();
            const source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);
            analyser.fftSize = 128;
            
            const dataArray = new Uint8Array(analyser.frequencyBinCount);
            const orb = document.querySelector('.siri-orb');
            
            function draw() {
                analyser.getByteFrequencyData(dataArray);
                let sum = dataArray.reduce((a, b) => a + b, 0);
                let scale = 0.8 + (sum / 2000);
                orb.style.transform = `scale(${scale})`;
                animationId = requestAnimationFrame(draw);
            }
            draw();
        } catch(e) { console.error("Mic error:", e); }
    }

    micBtn.onclick = async () => {
        isManuallyStopped = false;
        toggleMic(true);
        await startAudio();
        
        recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'vi-VN';
        
        // QUAN TRỌNG: Bật chế độ hiển thị kết quả tạm thời
        recognition.interimResults = true; 
        
        recognition.start();
        
        recognition.onresult = (e) => {
            let finalTranscript = '';
            let interimTranscript = '';

            // Duyệt qua các kết quả nhận diện
            for (let i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    finalTranscript += e.results[i][0].transcript;
                } else {
                    interimTranscript += e.results[i][0].transcript;
                }
            }

            // Ưu tiên hiển thị kết quả đang nói (interim), 
            // nếu không có thì hiển thị kết quả đã chốt (final)
            let result = interimTranscript || finalTranscript;
            
            // Cập nhật lên ô tìm kiếm và loại bỏ dấu câu cuối nếu có
            searchInput.value = result.trim().replace(/[.,?!]+$/, "");
        };
        
        searchInput.addEventListener('input', () => {
        // Nếu thanh tìm kiếm trống hoặc bị xóa hết nội dung
        if (searchInput.value === "") {
            // Hiện lại nút Mic nếu nó đang bị ẩn do nhận diện lỗi hoặc dừng giữa chừng
            if (micBtn.classList.contains('hidden')) {
                orbContainer.classList.add('hidden');
                micBtn.classList.remove('hidden');
                
                // Dừng mọi thứ liên quan đến thu âm nếu có
                if(animationId) cancelAnimationFrame(animationId);
                if(stream) stream.getTracks().forEach(t => t.stop());
            }
        }
    });
        
                recognition.onend = () => {
            // Chỉ hiện lại nút Mic nếu người dùng KHÔNG chủ động tắt
            if (!isManuallyStopped) {
                toggleMic(false);
            } else {
                // Nếu là tắt thủ công, bạn có thể giữ nguyên quả cầu 1 giây rồi cho nó ẩn đi
                orbContainer.classList.add('hidden');
                micBtn.classList.remove('hidden');
                isManuallyStopped = false; // Reset cờ cho lần sau
            }

            if(animationId) cancelAnimationFrame(animationId);
            if(stream) stream.getTracks().forEach(t => t.stop());
            if(audioContext) audioContext.close();
            
            // Kiểm tra để không submit khi tắt thủ công
            if(!isManuallyStopped && searchInput.value.trim() !== "") {
                searchForm.submit();
            }
        };
    };
});

function openFilterModal() { document.getElementById('filter-modal').classList.remove('hidden'); }
function closeFilterModal() { document.getElementById('filter-modal').classList.add('hidden'); }
