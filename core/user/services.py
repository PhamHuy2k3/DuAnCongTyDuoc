import re
import os
import unicodedata
import base64
import json
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime
from io import BytesIO
from PIL import Image
import logging
from decouple import config
import cv2
import numpy as np

logger = logging.getLogger('user')

try:
    import pytesseract
    # Windows: Cần set path đến tesseract.exe
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    OCR_ENGINE = 'pytesseract'
except ImportError:
    pytesseract = None
    OCR_ENGINE = None
    logger.warning("Tesseract not installed. OCR functionality will be limited.")

# Backup: EasyOCR (không cần cài Tesseract)
try:
    import easyocr
    if OCR_ENGINE is None:
        OCR_ENGINE = 'easyocr'
        # Khởi tạo reader một lần
        EASYOCR_READER = easyocr.Reader(['vi', 'en'], gpu=False)
except ImportError:
    easyocr = None
    if OCR_ENGINE is None:
        logger.error("No OCR engine available. Install pytesseract or easyocr.")


FIELDS = [
    'trade_name', 'active_ingredient', 'strength', 'dosage_form',
    'manufacturer', 'batch_number', 'registration_number',
    'mfg_date', 'exp_date', 'indications',
]


def nfc(s):
    return unicodedata.normalize('NFC', s)


VI = {'flags': re.I | re.UNICODE}

PATTERNS = {
    'trade_name': [
        re.compile(nfc(r'(?:Tên\s*(?:thương\s*mại|thuốc|biệt\s*dược|gốc)\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(nfc(r'(?:Thuốc\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(nfc(r'(?:Medicine|Drug|Product)\s*[:;.]?\s*(.+?)(?:\n|$)'), re.I),
    ],
    'active_ingredient': [
        re.compile(nfc(r'(?:Hoạt\s*chất\s*(?:chính)?\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(nfc(r'(?:Thành\s*phần\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(r'(?:Active\s*Ingredient|Composition)\s*[:;.]?\s*(.+?)(?:\n|$)', re.I),
    ],
    'strength': [
        re.compile(nfc(r'(?:Hàm\s*lượng\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(nfc(r'(?:Nồng\s*độ\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(r'\b(\d+(?:[.,]\d+)?\s*(?:mg|g|ml|mcg|µg|IU|%))\b', re.I),
    ],
    'dosage_form': [
        re.compile(nfc(r'(?:Dạng\s*bào\s*chế\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(nfc(r'(?:Dạng\s*dùng\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(r'(?:Dosage\s*Form)\s*[:;.]?\s*(.+?)(?:\n|$)', re.I),
    ],
    'manufacturer': [
        re.compile(nfc(r'(?:Nhà\s*sản\s*xuất\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(nfc(r'(?:Sản\s*xuất\s*bởi\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(r'(?:Manufacturer|Made\s*by)\s*[:;.]?\s*(.+?)(?:\n|$)', re.I),
    ],
    'batch_number': [
        re.compile(nfc(r'(?:Số\s*lô(?:\s*sản\s*xuất)?\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(r'(?:Lot|Batch|LOT|L\.?N\.?)\s*[:;.]?\s*(\S+)', re.I),
    ],
    'registration_number': [
        re.compile(nfc(r'(?:Số\s*đăng\s*ký(?:\s*lưu\s*hành)?\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(r'((?:VD|QLSP|SKĐK|SĐK)\s*[:-]?\s*[\d]+[\d-]*)', re.I | re.UNICODE),
        re.compile(r'(?:Reg\.?\s*No\.?)\s*[:;.]?\s*(.+?)(?:\n|$)', re.I),
    ],
    'mfg_date': [
        re.compile(nfc(r'(?:Ngày\s*sản\s*xuất\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(r'(?:NSX|SX|MFG|Mfg\.?\s*Date)\s*[:;.]?\s*(.+?)(?:\n|$)', re.I),
    ],
    'exp_date': [
        re.compile(nfc(r'(?:Hạn\s*sử\s*dụng\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(r'(?:HSD|Hạn|EXP|Exp\.?\s*Date|Expiry)\s*[:;.]?\s*(.+?)(?:\n|$)', re.I),
    ],
    'indications': [
        re.compile(nfc(r'(?:Chỉ\s*định\s*[:;.]?\s*)\s*(.+?)(?:\.\s*(?:Liều|Chống|Tác|Không|Thao)|(?:\n\s*\n)|$)'), re.I | re.UNICODE | re.DOTALL),
        re.compile(nfc(r'(?:Công\s*dụng\s*[:;.]?\s*)\s*(.+?)(?:\n|$)'), **VI),
        re.compile(r'(?:Indication|Use)\s*[:;.]?\s*(.+?)(?:\n|$)', re.I),
    ],
}


def extract_text_from_image_tesseract(image_path):
    try:
        img = Image.open(image_path)
        if img.mode != 'L':
            img = img.convert('L')
        text = pytesseract.image_to_string(img, lang='vie+eng', config='--psm 6')
        
        logger.info(f"Tesseract extracted {len(text)} characters from image")
        return nfc(text)
    except Exception as e:
        logger.error(f"Tesseract OCR error: {str(e)}")
        raise ValueError(f"Lỗi OCR với Tesseract: {str(e)}")


def extract_text_from_image_easyocr(image_path):
    try:
        results = EASYOCR_READER.readtext(image_path)
        
        # Ghép các dòng text lại
        text_lines = [result[1] for result in results]
        text = '\n'.join(text_lines)
        
        logger.info(f"EasyOCR extracted {len(text)} characters from image")
        return nfc(text)
    except Exception as e:
        logger.error(f"EasyOCR error: {str(e)}")
        raise ValueError(f"Lỗi OCR với EasyOCR: {str(e)}")


def extract_text_from_image(image_path):
    """Wrapper function để chọn OCR engine phù hợp"""
    if OCR_ENGINE == 'pytesseract' and pytesseract:
        return extract_text_from_image_tesseract(image_path)
    elif OCR_ENGINE == 'easyocr' and easyocr:
        return extract_text_from_image_easyocr(image_path)
    else:
        raise ValueError("Không có OCR engine nào được cài đặt. Vui lòng cài pytesseract hoặc easyocr.")


def parse_document(text):
    """Parse text và trích xuất thông tin thuốc"""
    text = nfc(text)
    result = {}
    scores = {}

    for field in FIELDS:
        patterns = PATTERNS.get(field, [])
        for i, pattern in enumerate(patterns):
            match = pattern.search(text)
            if match:
                value = match.group(1).strip()
                value = re.sub(r'\s+', ' ', value)
                
                # Validation
                if field == 'trade_name' and len(value) < 2:
                    continue
                if field == 'strength' and not any(c.isdigit() for c in value):
                    continue
                if field == 'batch_number' and len(value) > 50:
                    continue
                    
                if value:
                    result[field] = value
                    scores[field] = 1.0 - (i * 0.15)
                    break

    return result, scores


def calculate_accuracy(result, scores):
    """Tính độ chính xác dựa trên số fields được extract"""
    mandatory = ['trade_name', 'active_ingredient', 'batch_number', 'exp_date']
    optional = ['strength', 'dosage_form', 'manufacturer', 'registration_number', 'mfg_date', 'indications']

    found_mandatory = sum(1 for f in mandatory if f in result)
    found_optional = sum(1 for f in optional if f in result)

    score = (found_mandatory / len(mandatory)) * 0.7 + (found_optional / len(optional)) * 0.3
    return round(score * 100, 1)


def process_image(image_path):
    try:
        text = extract_text_from_image(image_path)
        
        if not text.strip():
            raise ValueError("Không thể đọc nội dung từ ảnh. Ảnh có thể quá mờ hoặc không có text.")
        result, scores = parse_document(text)
        accuracy = calculate_accuracy(result, scores)
        
        logger.info(f"OCR processed successfully. Accuracy: {accuracy}%")
        
        return {
            'data': result,
            'accuracy': accuracy,
            'scores': scores,
            'raw_text': text[:500],
            'ocr_engine': OCR_ENGINE
        }
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise


def validate_image_file(file):
    """Validate uploaded image file"""
    allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp']
    ext = file.name.split('.')[-1].lower()
    
    if ext not in allowed_extensions:
        raise ValueError(f"Chỉ chấp nhận file ảnh: {', '.join(allowed_extensions)}")
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024
    if file.size > max_size:
        raise ValueError("Kích thước ảnh không được vượt quá 10MB")
    
    return True


RECEIPT_WEIGHT_RE = re.compile(r'(?:(?:^|\s)N\s*)?(\d+[\.,]\d{3}\(\d+\))(?:\s*g\b|\s*$)', re.I)
RECEIPT_DATE_RE = re.compile(r'(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2})')
RECEIPT_BALANCE_RE = re.compile(r'Balance\s*Type\s+([A-Z0-9/._-]+)', re.I)
RECEIPT_SNR_RE = re.compile(r'SNR\s+([A-Z0-9]+)', re.I)


DEFAULT_RECEIPT_MODELS = [
    'deepseek-v4-flash-free',
    'gpt-4o-mini',
]

DEFAULT_GEMINI_MODELS = [
    'gemini-3.1-flash-lite',
    'gemini-3.0-flash',
]


def _load_receipt_image(image_path):
    image = Image.open(image_path)
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')
    grayscale = image.convert('L')
    return grayscale


def _build_receipt_data_uri(image_path):
    image = Image.open(image_path)
    if image.mode not in ('RGB', 'L'):
        image = image.convert('RGB')
        
    # Resize image if it's too large to prevent huge upload payload
    max_size = 1800
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=80)
    encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f'data:image/jpeg;base64,{encoded}'


def _load_receipt_vision_config():
    api_key = (
        config('OPENCODEZEN_API_KEY', default='').strip()
        or config('OPENAI_API_KEY', default='').strip()
    )
    base_url = config('OPENCODEZEN_BASE_URL', default='https://api.opencode.ai/v1').strip().rstrip('/')
    models = (
        config('OPENCODEZEN_MODELS', default='deepseek-v4-flash,gpt-4o-mini').strip()
        or config('OPENAI_MODELS', default='').strip()
    )
    model_list = [model.strip() for model in models.split(',') if model.strip()]
    if not model_list:
        model_list = ['deepseek-v4-flash', 'gpt-4o-mini']
    return api_key, base_url, model_list


def _load_gemini_vision_config():
    api_key = config('GEMINI_API_KEY', default='').strip()
    base_url = config('GEMINI_BASE_URL', default='https://generativelanguage.googleapis.com/v1beta').strip().rstrip('/')
    models = config('GEMINI_MODELS', default='').strip()
    model_list = [model.strip() for model in models.split(',') if model.strip()]
    if not model_list:
        model_list = DEFAULT_GEMINI_MODELS
    return api_key, base_url, model_list


def _extract_json_object(text):
    text = (text or '').strip()
    if not text:
        return None

    # Strip markdown code blocks
    if text.startswith('```'):
        lines = text.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        text = '\n'.join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON object via regex
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Attempt cleaning trailing commas in arrays/objects
            json_str_clean = re.sub(r',\s*([\]}])', r'\1', json_str)
            # Remove control characters like unescaped raw newlines in string values
            json_str_clean = re.sub(r'\n\s*', r' ', json_str_clean)
            try:
                return json.loads(json_str_clean)
            except json.JSONDecodeError:
                pass
    return None


def _call_receipt_vision_model(image_data_uri, model, base_url, api_key):
    payload = {
        'model': model,
        'messages': [
            {
                'role': 'system',
                'content': (
                    'You are a vision OCR engine for a laboratory balance receipt. '
                    'Return only JSON with a records array. Each record must have weight, datetime, balance_type, snr, and is_partial. '
                    'Read the left column top-to-bottom first, then the right column top-to-bottom. '
                    'Keep exact numeric text, including parentheses, and never round values. '
                    'Do not invent missing digits. Ignore handwritten signatures and decorative marks.'
                ),
            },
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': (
                            'Extract the receipt text from this two-column balance printout. '\
                            'Preserve the exact weight format such as 0.256(1) g. '\
                            'Return records in reading order and include partial records when a block is split across columns.'
                        ),
                    },
                    {
                        'type': 'image_url',
                        'image_url': {'url': image_data_uri},
                    },
                ],
            },
        ],
        'temperature': 0,
        'response_format': {'type': 'json_object'},
        'max_tokens': 4000,
    }

    request = urllib.request.Request(
        f'{base_url}/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            response_body = response.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode('utf-8', errors='replace') if exc.fp else ''
        raise ValueError(f'Vision API HTTP {exc.code}: {error_body or exc.reason}') from exc
    except urllib.error.URLError as exc:
        raise ValueError(f'Vision API connection error: {exc.reason}') from exc

    response_json = json.loads(response_body)
    content = ''
    if isinstance(response_json, dict):
        choices = response_json.get('choices') or []
        if choices:
            message = choices[0].get('message') or {}
            content = message.get('content') or ''
        elif 'content' in response_json:
            content = response_json.get('content') or ''

    parsed = _extract_json_object(content)
    if parsed is None:
        parsed = _extract_json_object(response_body)
    if parsed is None:
        raise ValueError('Model vision response did not contain valid JSON')

    return parsed


def _call_receipt_gemini_model(image_data_uri, model, base_url, api_key):
    mime_type = 'image/png'
    if image_data_uri.startswith('data:'):
        header, encoded = image_data_uri.split(',', 1)
        mime_type = header.split(';')[0].split(':')[1]
        image_base64 = encoded
    else:
        image_base64 = image_data_uri

    payload = {
        'contents': [
            {
                'role': 'user',
                'parts': [
                    {
                        'text': (
                            'Extract the receipt text from this two-column balance printout.\n'
                            'The left column and right column are two separate physical tapes. Do NOT stitch, merge, or pair any records across columns.\n'
                            'Read the left column top-to-bottom first, then the right column top-to-bottom.\n'
                            'CRITICAL: Each measurement is a block separated by dashed lines.\n'
                            '- The very first block at the top of a column has only datetime/metadata but NO weight. You MUST set weight to null for this block. Do NOT pair it with the weight of the second block.\n'
                            '- The very last block at the bottom of a column may have only a weight but NO datetime/metadata. You MUST set datetime/metadata to null for this block.\n'
                            'Preserve the exact weight format like 0.256(1) g.\n'
                            'Return JSON only with a records array.'
                        )
                    },
                    {
                        'inline_data': {
                            'mime_type': mime_type,
                            'data': image_base64,
                        }
                    }
                ]
            }
        ],
        'generationConfig': {
            'temperature': 0,
            'responseMimeType': 'application/json',
            'maxOutputTokens': 8192,
        },
        'systemInstruction': {
            'parts': [
                {
                    'text': (
                        'You are a vision OCR engine for a laboratory balance receipt.\n'
                        'CRITICAL VALIDATION:\n'
                        '- First, analyze if the image actually contains a laboratory balance printout tape (characterized by a vertical white paper strip, weight lines starting with "N" and ending with "g", dashed separator lines "----", and balance metadata like "Balance Type", "SNR").\n'
                        '- If the image is completely unrelated (e.g. it is a landscape, a cat, a person, a document of another type, or random text without balance printout patterns), you MUST return a JSON object with: {"error_code": "unrelated_image"}.\n'

                        'NORMAL EXTRACTION:\n'
                        '- If it is a valid receipt, return JSON with a records array. Each record must have weight, datetime, balance_type, snr.\n'
                        '- If a block has no weight, set weight to null. If a block has no datetime/metadata, set datetime/balance_type/snr to null.\n'
                        '- Never pair metadata from one block with weight from another block. Read top-to-bottom.'
                    )
                }
            ]
        }
    }

    request = urllib.request.Request(
        f'{base_url}/models/{model}:generateContent?key={api_key}',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        },
        method='POST',
    )

    with urllib.request.urlopen(request, timeout=45) as response:
        response_body = response.read().decode('utf-8')

    response_json = json.loads(response_body)
    content = ''
    candidates = response_json.get('candidates') or []
    if candidates:
        content_parts = ((candidates[0].get('content') or {}).get('parts') or [])
        if content_parts:
            content = content_parts[0].get('text') or ''

    logger.info(f"Gemini model {model} raw response text: {content}")
    parsed = _extract_json_object(content)
    if parsed is None:
        parsed = _extract_json_object(response_body)
    if parsed is None:
        raise ValueError('Model vision response did not contain valid JSON')

    logger.info(f"Gemini model {model} successfully parsed JSON: {parsed}")
    return parsed


def _normalize_receipt_line(text):
    text = nfc(text or '')
    text = text.replace('\x0c', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _extract_receipt_words(image):
    if not pytesseract:
        raise ValueError("Tesseract OCR chưa được cài đặt")

    data = pytesseract.image_to_data(
        image,
        lang='eng+vie',
        config='--oem 3 --psm 6',
        output_type=pytesseract.Output.DICT,
    )

    line_map = defaultdict(list)
    count = len(data.get('text', []))
    for idx in range(count):
        text = (data['text'][idx] or '').strip()
        if not text:
            continue
        try:
            conf = float(data['conf'][idx]) if data['conf'][idx] not in ('', '-1') else -1.0
        except Exception:
            conf = -1.0
        if conf < 0:
            continue

        key = (
            data.get('page_num', [1])[idx],
            data.get('block_num', [0])[idx],
            data.get('par_num', [0])[idx],
            data.get('line_num', [0])[idx],
        )
        left = int(data.get('left', [0])[idx])
        top = int(data.get('top', [0])[idx])
        width = int(data.get('width', [0])[idx])
        height = int(data.get('height', [0])[idx])
        line_map[key].append({
            'text': text,
            'left': left,
            'top': top,
            'right': left + width,
            'bottom': top + height,
        })

    lines = []
    for key, words in line_map.items():
        words.sort(key=lambda item: item['left'])
        line_text = _normalize_receipt_line(' '.join(item['text'] for item in words))
        if not line_text:
            continue

        left = min(item['left'] for item in words)
        top = min(item['top'] for item in words)
        right = max(item['right'] for item in words)
        bottom = max(item['bottom'] for item in words)
        lines.append({
            'text': line_text,
            'left': left,
            'top': top,
            'right': right,
            'bottom': bottom,
        })

    image_width = image.width
    for line in lines:
        center_x = (line['left'] + line['right']) / 2.0
        line['column'] = 0 if center_x < (image_width / 2.0) else 1

    lines.sort(key=lambda item: (item['column'], item['top'], item['left']))
    return lines


def _extract_receipt_weight(text):
    match = RECEIPT_WEIGHT_RE.search(text)
    if not match:
        return None
    value = match.group(1).replace(' ', '')
    value = value.replace(',', '.')
    return value


def _extract_receipt_datetime(text):
    match = RECEIPT_DATE_RE.search(text)
    return match.group(1) if match else None


def _extract_receipt_balance_type(text):
    match = RECEIPT_BALANCE_RE.search(text)
    return match.group(1) if match else None


def _extract_receipt_snr(text):
    match = RECEIPT_SNR_RE.search(text)
    return match.group(1) if match else None


def _finalize_receipt_record(record):
    normalized = {
        'weight': record.get('weight', '').strip(),
        'datetime': record.get('datetime', '').strip(),
        'balance_type': record.get('balance_type', '').strip(),
        'snr': record.get('snr', '').strip(),
    }

    normalized['is_partial'] = not all(normalized.values())
    return normalized


def _normalize_vision_records(records):
    normalized_records = []
    for record in records or []:
        if isinstance(record, str):
            continue
        weight_str = str(record.get('weight') or '').strip()
        weight_str = re.sub(r'\s*[gG]$', '', weight_str)
        normalized = {
            'weight': weight_str,
            'datetime': str(record.get('datetime') or '').strip(),
            'balance_type': str(record.get('balance_type') or '').strip(),
            'snr': str(record.get('snr') or '').strip(),
        }
        normalized['is_partial'] = bool(record.get('is_partial', not all([normalized['weight'], normalized['datetime'], normalized['balance_type'], normalized['snr']])))
        if normalized['weight'] or normalized['datetime'] or normalized['balance_type'] or normalized['snr']:
            normalized_records.append(normalized)
    return normalized_records


def extract_balance_receipt_records(image_path):
    """Extract balance-printout records using a Gemini vision model, then normalize and stitch split blocks."""
    gemini_key, gemini_base_url, gemini_models = _load_gemini_vision_config()

    if not gemini_key:
        raise ValueError('Chưa cấu hình GEMINI_API_KEY trong file .env')

    image_data_uri = _build_receipt_data_uri(image_path)
    last_error = None
    has_success = False

    import time
    for model in gemini_models:
        try:
            result = _call_receipt_gemini_model(image_data_uri, model, gemini_base_url, gemini_key)
            has_success = True
            
            # If the result contains a validation error code, return it directly
            if isinstance(result, dict) and 'error_code' in result:
                return result
                
            records = result.get('records', []) if isinstance(result, dict) else []
            normalized_records = _normalize_vision_records(records)
            if normalized_records:
                return normalized_records
        except Exception as exc:
            last_error = exc
            logger.warning(f'Receipt Gemini model {model} failed: {exc}')
            time.sleep(1.5)

    if not has_success and last_error:
        raise ValueError(f'Không thể trích xuất dữ liệu bằng vision API: {last_error}')

    return []


def analyze_blur_and_regions(image_file):
    """
    Analyzes the image for blurriness globally and locally.
    Returns: (is_blurry, global_variance, blurred_regions)
    """
    try:
        image_file.seek(0)
        file_bytes = np.frombuffer(image_file.read(), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img is None:
            return False, 0.0, []
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        global_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # 1. Global blur check: Extremely blurry images have very low variance
        if global_var < 50.0:
            return True, global_var, [{'x': 0, 'y': 0, 'w': 100, 'h': 100}]
        
        # 2. Local grid analysis with Relative Variance Bounding
        grid_rows, grid_cols = 12, 12
        block_h, block_w = h // grid_rows, w // grid_cols
        active_blocks = []
        
        for r in range(grid_rows):
            for c in range(grid_cols):
                y1, y2 = r * block_h, (r + 1) * block_h
                x1, x2 = c * block_w, (c + 1) * block_w
                block = gray[y1:y2, x1:x2]
                
                block_std = np.std(block)
                # If std > 12.0, block contains high contrast content (text)
                if block_std > 12.0:
                    block_var = cv2.Laplacian(block, cv2.CV_64F).var()
                    active_blocks.append({
                        'r': r, 'c': c, 'var': block_var,
                        'x_pct': (x1 / w) * 100, 'y_pct': (y1 / h) * 100,
                        'w_pct': ((x2 - x1) / w) * 100, 'h_pct': ((y2 - y1) / h) * 100
                    })
        
        blurred_regions = []
        active_count = len(active_blocks)
        is_blurry = False
        
        if active_count > 0:
            max_var = max([b['var'] for b in active_blocks])
            # Dynamic threshold: bounded between 30 and 120, adjusting to image sharpness
            blur_thresh = min(max(0.02 * max_var, 30.0), 120.0)
            
            for b in active_blocks:
                if b['var'] < blur_thresh:
                    blurred_regions.append({
                        'x': round(b['x_pct'], 2),
                        'y': round(b['y_pct'], 2),
                        'w': round(b['w_pct'], 2),
                        'h': round(b['h_pct'], 2)
                    })
                    
            blur_ratio = len(blurred_regions) / active_count
            if blur_ratio >= 0.25 and active_count >= 5:
                is_blurry = True
        
        return is_blurry, global_var, blurred_regions
        
    except Exception as e:
        logger.error(f"Error in blur detection: {str(e)}")
        return False, 0.0, []
        
    except Exception as e:
        logger.error(f"Error in blur detection: {str(e)}")
        return False, 0.0, []

def analyze_image_quality_with_ai(image_file):
    """
    Uses Gemini 2.0 Flash to strictly evaluate image quality (blur/unrelated)
    WITHOUT attempting to extract text, to prevent hallucinations.
    Returns: 'clear', 'blurry', or 'unrelated'
    """
    try:
        api_key, base_url, model_list = _load_gemini_vision_config()
        if not api_key:
            return 'clear'
            
        image_file.seek(0)
        image_data_uri = _build_receipt_data_uri(image_file)
        
        header, encoded = image_data_uri.split(',', 1)
        mime_type = header.split(';')[0].split(':')[1]
        
        payload = {
            'contents': [
                {
                    'role': 'user',
                    'parts': [
                        {
                            'text': (
                                'Evaluate the image. Answer in JSON with {"status": "result"} where result is ONE of:\n'
                                '- "unrelated": if the image is NOT a laboratory balance printout (e.g., people, landscapes, normal documents).\n'
                                '- "blurry": if ANY PART of the text is blurred, out of focus, has glare, or if ANY numbers are illegible. Even if some parts are clear, if OTHER parts are illegible due to blur or glare, you MUST return "blurry". DO NOT guess.\n'
                                '- "clear": ONLY if ALL numbers and text on the entire printout are perfectly clear and easily readable.'
                            )
                        },
                        {
                            'inline_data': {
                                'mime_type': mime_type,
                                'data': encoded,
                            }
                        }
                    ]
                }
            ],
            'generationConfig': {
                'temperature': 0,
                'responseMimeType': 'application/json',
                'maxOutputTokens': 128,
            }
        }
        
        import time
        last_error = None
        for model in model_list:
            retries = 3
            for attempt in range(retries):
                try:
                    request = urllib.request.Request(
                        f'{base_url}/models/{model}:generateContent?key={api_key}',
                        data=json.dumps(payload).encode('utf-8'),
                        headers={
                            'Content-Type': 'application/json',
                        },
                        method='POST',
                    )
                    
                    with urllib.request.urlopen(request, timeout=25) as response:
                        response_body = response.read().decode('utf-8')
                        
                    response_json = json.loads(response_body)
                    response_content = ''
                    candidates = response_json.get('candidates') or []
                    if candidates:
                        parts = (candidates[0].get('content') or {}).get('parts') or []
                        if parts:
                            response_content = parts[0].get('text') or ''
                            
                    parsed = _extract_json_object(response_content)
                    if parsed and 'status' in parsed:
                        status = parsed['status'].lower()
                        if status in ['unrelated', 'blurry', 'clear']:
                            logger.info(f"AI Quality filter determined status '{status}' using model {model}")
                            return status
                            
                    break # If JSON parsing fails, breaking to next model
                    
                except urllib.error.HTTPError as e:
                    last_error = e
                    if e.code == 429:
                        logger.warning(f"AI Quality filter 429 on model {model}, attempt {attempt+1}/{retries}. Waiting...")
                        time.sleep(2.0)
                        continue
                    else:
                        logger.warning(f"AI Quality filter HTTP {e.code} on model {model}: {str(e)}")
                        break # Other HTTP errors -> try next model
                except Exception as e:
                    logger.warning(f"AI Quality filter failed on model {model}: {str(e)}")
                    last_error = e
                    break # Other errors -> try next model
                
        if last_error:
            logger.error(f"AI Quality filter exhausted all models and retries. Last error: {str(last_error)}")
            return 'error' # Return error so we don't hallucinate
            
        return 'error'
    except Exception as e:
        logger.error(f"AI Quality filter critical error: {str(e)}")
        return 'clear'
