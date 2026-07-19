import re
import codecs

with codecs.open('core/user/templates/user/scan.html', 'r', 'utf-8') as f:
    content = f.read()

# 1. Remove scan mode tabs (lines 234-245 approx)
content = re.sub(
    r'<!-- Scan mode switcher tabs -->[\s\S]*?</div>\s*<!-- 1\. WORD TEMPLATE SELECTOR VIEW',
    r'<!-- 1. WORD TEMPLATE SELECTOR VIEW',
    content
)

# 2. Remove word templates selection
content = re.sub(
    r'<!-- 1\. WORD TEMPLATE SELECTOR VIEW \(Shown in Word Tab Mode\) -->[\s\S]*?<!-- 2\. PHOTO SELECTOR INSTRUCTIONS',
    r'<!-- 2. PHOTO SELECTOR INSTRUCTIONS',
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
    r'<!-- A\. PANEL 1: DRUG INFO FORM \(Shown in Word Tab Mode\) -->[\s\S]*?<!-- B\. PANEL 2: WEIGHT UNIFORMITY 20 PILLS FORM',
    r'<!-- B. PANEL 2: WEIGHT UNIFORMITY 20 PILLS FORM',
    content
)

# 7. Unhide photo form panel
content = content.replace('<div id="panel-photo-form" class="hidden">', '<div id="panel-photo-form">')

with codecs.open('core/user/templates/user/scan.html', 'w', 'utf-8') as f:
    f.write(content)

print("scan.html safely updated")
