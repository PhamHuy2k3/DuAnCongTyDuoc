# HƯỚNG DẪN CÀI ĐẶT OCR CHO QUÉT ẢNH

## Lựa chọn 1: Tesseract OCR (Khuyến nghị - Nhẹ và nhanh)

### Bước 1: Cài Tesseract-OCR
Download và cài đặt Tesseract từ:
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- Chọn file: `tesseract-ocr-w64-setup-5.x.x.exe`
- Khi cài, check option "Additional language data" và chọn **Vietnamese**

### Bước 2: Cài Python package
```bash
pip install pytesseract Pillow
```

### Bước 3: Cấu hình path (Windows)
Thêm vào `user/services.py` sau dòng `import pytesseract`:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Bước 4: Kiểm tra cài đặt
```bash
tesseract --version
```

---

## Lựa chọn 2: EasyOCR (Dễ cài nhưng nặng ~500MB)

### Ưu điểm:
- Không cần cài Tesseract riêng
- Chính xác hơn với ảnh chất lượng kém
- Hỗ trợ nhiều ngôn ngữ tốt hơn

### Nhược điểm:
- Download models ~500MB lần đầu
- Chậm hơn Tesseract
- Cần RAM nhiều hơn

### Cài đặt:
```bash
pip install easyocr torch torchvision
```

### Sử dụng:
Trong `requirements.txt`, comment Tesseract và uncomment EasyOCR:
```
# pytesseract>=0.3.10
easyocr>=1.7.0
torch>=2.0.0
torchvision>=0.15.0
```

---

## Test OCR

### Test với Tesseract:
```python
from PIL import Image
import pytesseract

# Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img = Image.open('test_image.jpg')
text = pytesseract.image_to_string(img, lang='vie+eng')
print(text)
```

### Test với EasyOCR:
```python
import easyocr

reader = easyocr.Reader(['vi', 'en'], gpu=False)
results = reader.readtext('test_image.jpg')

for result in results:
    print(result[1])  # In ra text
```

---

## Format ảnh hỗ trợ
- JPG/JPEG
- PNG
- BMP
- TIFF
- WEBP

---

## Tips để OCR chính xác:

1. **Chất lượng ảnh**:
   - Độ phân giải cao (min 300 DPI)
   - Ánh sáng tốt, không mờ
   - Chữ rõ ràng, không bị che

2. **Góc chụp**:
   - Chụp thẳng, không nghiêng
   - Đầy đủ nội dung
   - Không bị lóa/tối

3. **Preprocessing** (nếu ảnh xấu):
   - Convert sang grayscale
   - Tăng contrast
   - Denoise
   - Deskew (xoay thẳng)

---

## Xử lý lỗi thường gặp

### Lỗi: "Tesseract not found"
```python
# Thêm vào services.py
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Lỗi: "Vietnamese language not found"
- Cài lại Tesseract và chọn Vietnamese language pack
- Hoặc download `vie.traineddata` từ: https://github.com/tesseract-ocr/tessdata
- Copy vào: `C:\Program Files\Tesseract-OCR\tessdata\`

### Lỗi: EasyOCR quá chậm
- Sử dụng `gpu=True` nếu có GPU NVIDIA
- Hoặc switch sang Tesseract

---

## So sánh

| Tiêu chí | Tesseract | EasyOCR |
|----------|-----------|---------|
| Tốc độ | Nhanh (~1-2s) | Chậm (~5-10s) |
| Kích thước | ~5MB | ~500MB |
| Cài đặt | Cần cài riêng | Chỉ pip install |
| Chính xác | Tốt với ảnh rõ | Tốt với ảnh xấu |
| RAM | ~100MB | ~500MB-1GB |
| Tiếng Việt | Tốt | Rất tốt |

---

## Khuyến nghị:

- **Development/Testing**: Dùng Tesseract (nhanh, nhẹ)
- **Production với ảnh chất lượng cao**: Tesseract
- **Production với ảnh chất lượng thấp/mobile**: EasyOCR
- **Server có GPU**: EasyOCR với GPU=True

---

## Cải thiện độ chính xác

Nếu OCR không chính xác, có thể:

1. Thêm preprocessing trong `services.py`:
```python
from PIL import ImageEnhance, ImageFilter

def preprocess_image(img):
    # Convert to grayscale
    img = img.convert('L')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    
    return img
```

2. Điều chỉnh Tesseract config:
```python
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐ'
text = pytesseract.image_to_string(img, lang='vie+eng', config=custom_config)
```

3. Train custom Tesseract model cho font chữ đặc biệt

---

**Sau khi cài đặt xong, test ngay với một ảnh mẫu!**
