import re
import codecs

with codecs.open('core/coreapp/static/coreapp/js/main.js', 'r', 'utf-8') as f:
    js = f.read()

# 1. Remove scan mode toggle events
js = re.sub(r'// Toggle Modes \(Word vs Photo Scanner\)[\s\S]*?// Mock Documents Database', '// Mock Documents Database', js)

# 2. Remove word mockDocuments & loadDocumentState
js = re.sub(r'// Mock Documents Database[\s\S]*?// Set selected document preview on paper mockup[\s\S]*?function loadDocumentState\(key\) \{[\s\S]*?\}\n\n    // Connect Quick templates button events', '// Connect Quick templates button events', js)

# 3. Fix simulateCustomFileUpload
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

# 4. Fix btnStartProcess
# We need to extract the 'else' block from btnStartProcess.addEventListener
js = re.sub(r'if \(currentScanMode === \'word\'\) \{[\s\S]*?\} else \{\s*// PHOTO OCR BALANCE RECEIPT MODE', r'// PHOTO OCR BALANCE RECEIPT MODE', js)

# 5. Remove finishScanningProcess (word version)
js = re.sub(r'function finishScanningProcess\(\) \{[\s\S]*?\}\n\n    function finishPhotoScanningProcess\(\) \{', r'function finishPhotoScanningProcess() {', js)

# 6. Remove any remaining btnTabWord / btnTabPhoto references
js = re.sub(r'btnTabWord\..*?;', '', js)
js = re.sub(r'btnTabPhoto\..*?;', '', js)
js = re.sub(r'const btnTabWord.*?;', '', js)
js = re.sub(r'const btnTabPhoto.*?;', '', js)
js = re.sub(r'const wordTemplatesBlock.*?;', '', js)
js = re.sub(r'const panelWordForm.*?;', '', js)

js = js.replace("let currentScanMode = 'word';", "let currentScanMode = 'photo';")

with codecs.open('core/coreapp/static/coreapp/js/main.js', 'w', 'utf-8') as f:
    f.write(js)
print("main.js safely updated")
