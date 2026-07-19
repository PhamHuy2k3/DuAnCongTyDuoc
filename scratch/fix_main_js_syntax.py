import re
import codecs

with codecs.open('core/coreapp/static/coreapp/js/main.js', 'r', 'utf-8') as f:
    js = f.read()

# Remove the extra `}` before `});` in btnStartProcess
js = re.sub(r'runGeminiOCR\(selectedFile\);\s*\}\s*\}\s*\}\);', r'runGeminiOCR(selectedFile);\n            }\n    });', js)

# Fix updateDropzoneText
new_updateDropzoneText = """
    function updateDropzoneText(mode) {
        const titleEl = document.getElementById('dropzone-title-main');
        const supportEl = document.getElementById('dropzone-support-main');
        const photoHints = document.getElementById('dropzone-photo-hints');
        if (!titleEl || !supportEl) return;
        
        titleEl.textContent = 'Kéo & Thả nhiều ảnh Phiếu Cân ở đây';
        supportEl.textContent = 'Hỗ trợ các định dạng: .jpg, .jpeg, .png';
        if (photoHints) photoHints.classList.remove('hidden');
    }
"""
js = re.sub(r'function updateDropzoneText\(mode\) \{[\s\S]*?\}\s*\}', new_updateDropzoneText, js)

with codecs.open('core/coreapp/static/coreapp/js/main.js', 'w', 'utf-8') as f:
    f.write(js)
print("Syntax fixed")
