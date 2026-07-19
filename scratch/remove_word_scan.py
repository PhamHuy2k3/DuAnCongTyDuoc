import re
import codecs

with codecs.open('core/user/templates/user/scan.html', 'r', 'utf-8') as f:
    content = f.read()

# 1. Remove scan mode tabs
content = re.sub(
    r'<!-- Scan mode switcher tabs -->[\s\S]*?</div>\s*<!-- 1. WORD TEMPLATE',
    r'<!-- 1. WORD TEMPLATE',
    content
)

# 2. Remove word templates selection
content = re.sub(
    r'<!-- 1. WORD TEMPLATE SELECTOR VIEW.*?<div id="word-templates-selection">[\s\S]*?</div>\s*</div>\s*<!-- 2. PHOTO SELECTOR',
    r'<!-- 2. PHOTO SELECTOR',
    content
)

# 3. Unhide photo templates selection
content = content.replace('<div id="photo-templates-selection" class="hidden">', '<div id="photo-templates-selection">')

# 4. Remove word file loaded view
content = re.sub(
    r'<!-- B\. File Loaded State \(Word preview\) -->[\s\S]*?<!-- C\. Photo Loaded State',
    r'<!-- C. Photo Loaded State',
    content
)

# 5. Update dropzone prompt
content = content.replace('Kéo & Thả file Word ở đây', 'Kéo & Thả nhiều ảnh Phiếu Cân ở đây')
content = content.replace('Hỗ trợ các định dạng: .docx, .doc, .pdf', 'Hỗ trợ các định dạng: .jpg, .jpeg, .png')
content = content.replace('id="dropzone-photo-hints" class="hidden"', 'id="dropzone-photo-hints"')
content = content.replace('accept=".docx,.doc,.pdf,.txt,.jpg,.jpeg,.png"', 'accept=".jpg,.jpeg,.png"')

# 6. Remove panel-word-form
content = re.sub(
    r'<!-- A\. PANEL 1: DRUG INFO FORM \(Shown in Word Tab Mode\) -->[\s\S]*?<!-- B\. PANEL 2: UNIFORMITY WEIGHT FORM',
    r'<!-- B. PANEL 2: UNIFORMITY WEIGHT FORM',
    content
)

with codecs.open('core/user/templates/user/scan.html', 'w', 'utf-8') as f:
    f.write(content)

print("scan.html updated")

# Now update main.js
with codecs.open('core/coreapp/static/coreapp/js/main.js', 'r', 'utf-8') as f:
    js_content = f.read()

# 1. We just want to remove the Word toggle logic or hardcode it to photo mode
# Let's remove btnTabWord and btnTabPhoto logic
js_content = re.sub(r'// Toggle Modes \(Word vs Photo Scanner\)[\s\S]*?// Mock Documents Database', '// Mock Documents Database', js_content)

# We can also remove mockDocuments
js_content = re.sub(r'// Mock Documents Database[\s\S]*?// Set selected document preview on paper mockup', '// Set selected document preview on paper mockup', js_content)

js_content = js_content.replace("let currentScanMode = 'word';", "let currentScanMode = 'photo';")

# Let's write the js back
with codecs.open('core/coreapp/static/coreapp/js/main.js', 'w', 'utf-8') as f:
    f.write(js_content)
print("main.js updated")
