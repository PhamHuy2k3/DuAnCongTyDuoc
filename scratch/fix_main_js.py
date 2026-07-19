import re
import codecs

with codecs.open('core/coreapp/static/coreapp/js/main.js', 'r', 'utf-8') as f:
    js = f.read()

# 1. Remove references to btnTabWord and btnTabPhoto
js = js.replace("const btnTabWord = document.getElementById('btn-tab-word');", "")
js = js.replace("const btnTabPhoto = document.getElementById('btn-tab-photo');", "")

# 2. In simulateCustomFileUpload, remove the btnTabPhoto.click() and word logic
# Replace the whole function content
new_simulate = """
    function simulateCustomFileUpload(fileName) {
        if (isProcessing) return;
        
        const nameLower = fileName.toLowerCase();
        // Check if user uploaded a photo of balance receipt (jpg, png)
        if (nameLower.endsWith('.jpg') || nameLower.endsWith('.jpeg') || nameLower.endsWith('.png')) {
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

        addLog(`File format not supported. Please upload an image (.jpg, .png).`, 'error');
    }
"""
js = re.sub(r'function simulateCustomFileUpload\(fileName\) \{[\s\S]*?\n    \}', new_simulate, js)

# 3. Remove word branch in btnStartProcess
# It has: if (currentScanMode === 'word') { ... } else { ... }
js = re.sub(r'if \(currentScanMode === \'word\'\) \{[\s\S]*?\} else \{(\s*// PHOTO OCR BALANCE RECEIPT MODE)', r'\1', js)
# Also remove updateWordScan function if left
js = re.sub(r'function updateWordScan\(currentTime\) \{[\s\S]*?\} else \{[\s\S]*?finishScanningProcess\(\);[\s\S]*?\}', '', js)

# 4. Remove btnTabWord / btnTabPhoto disable/enable lines anywhere
js = re.sub(r'btnTabWord\..*?;', '', js)
js = re.sub(r'btnTabPhoto\..*?;', '', js)

# 5. Remove updateDropzoneText word logic
js = re.sub(r'function updateDropzoneText\(mode\) \{[\s\S]*?\} else \{', 'function updateDropzoneText(mode) {', js)

with codecs.open('core/coreapp/static/coreapp/js/main.js', 'w', 'utf-8') as f:
    f.write(js)
print("main.js fixed")
