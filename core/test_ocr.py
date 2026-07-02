# -*- coding: utf-8 -*-
"""
Script test OCR engine
Chay: python test_ocr.py
"""

import sys

print("=== Testing OCR Setup ===\n")

# Test 1: Check pytesseract
print("1. Checking pytesseract...")
try:
    import pytesseract
    print("   [OK] pytesseract installed")
except ImportError:
    print("   [ERROR] pytesseract NOT installed")
    print("   Run: pip install pytesseract")
    sys.exit(1)

# Test 2: Check Pillow
print("\n2. Checking Pillow...")
try:
    from PIL import Image
    print("   [OK] Pillow installed")
except ImportError:
    print("   [ERROR] Pillow NOT installed")
    print("   Run: pip install Pillow")
    sys.exit(1)

# Test 3: Check Tesseract executable
print("\n3. Checking Tesseract executable...")
try:
    version = pytesseract.get_tesseract_version()
    print(f"   [OK] Tesseract version: {version}")
except Exception as e:
    print(f"   [ERROR] Tesseract NOT found: {e}")
    print("\n   HUONG DAN CAI DAT:")
    print("   - Download: https://github.com/UB-Mannheim/tesseract/wiki")
    print("   - Cai dat va chon Vietnamese language pack")
    print("   - Sau do them vao user/services.py:")
    print("     pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
    sys.exit(1)

# Test 4: Check languages
print("\n4. Checking available languages...")
try:
    langs = pytesseract.get_languages()
    print(f"   Available: {', '.join(langs)}")
    
    if 'vie' in langs or 'Vietnamese' in langs:
        print("   [OK] Vietnamese language available")
    else:
        print("   [WARNING] Vietnamese language NOT found")
        print("   Download vie.traineddata from:")
        print("   https://github.com/tesseract-ocr/tessdata")
        
    if 'eng' in langs or 'English' in langs:
        print("   [OK] English language available")
        
except Exception as e:
    print(f"   [WARNING] Could not get languages: {e}")

print("\n" + "="*40)
print("OCR Setup Status: READY")
print("="*40)
print("\nBan co the bat dau su dung tinh nang quet anh!")
print("Upload anh chua thong tin thuoc (JPG, PNG, etc.)")
