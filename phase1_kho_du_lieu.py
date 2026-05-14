import pandas as pd
import json
import re

def clean_cas(text):
    """Giữ lại mã CAS chuẩn định dạng XXX-XX-X"""
    if not text or pd.isna(text): return ""
    match = re.search(r'\d{2,7}-\d{2}-\d', str(text))
    return match.group(0) if match else ""

def solve_phase1(file_path):
    print(f"--- Bắt đầu Phase 1: Xử lý file {file_path} ---")
    
    try:
        # Đọc file (Hỗ trợ Excel)
        df = pd.read_excel(file_path)
        
        # Làm sạch các cột quan trọng
        df['CAS_Clean'] = df['Mã CAS'].apply(clean_cas)
        
        # Logic phân loại tự động dựa trên từ khóa trong tệp pháp lý
        def auto_classify(row):
            phap_ly = str(row.get('Căn cứ pháp lý', '')).lower()
            if any(k in phap_ly for k in ['cấm', 'bảng 1']):
                return 'BANNED' (Cấm)
            if any(k in phap_ly for k in ['tiền chất', 'precursor']):
                return 'PRECURSOR' (Tiền chất)
            if any(k in phap_ly for k in ['khai báo', 'phụ lục v']):
                return 'DECLARATION' (Khai báo)
            return 'NORMAL' (Bình thường)

        # Tạo cấu trúc dữ liệu nén JSON
        db = []
        for _, row in df.iterrows():
            item = {
                "vn_name": str(row.get('Tên hóa chất (Tiếng Việt)', '')).strip(),
                "en_name": str(row.get('Tên hóa chất (Tiếng Anh)', '')).strip(),
                "cas": clean_cas(row.get('Mã CAS', '')),
                "hs_code": str(row.get('Mã HS', '')).replace('.', '').strip(),
                "legal_basis": str(row.get('Căn cứ pháp lý', '')),
                "type": auto_classify(row)
            }
            if item['cas']: # Chỉ lưu những chất có mã CAS để đối chiếu
                db.append(item)

        # Lưu thành file database.json
        with open('database.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
            
        print(f"--- Hoàn thành! Đã trích xuất {len(db)} hóa chất vào database.json ---")
        return True

    except Exception as e:
        print(f"Lỗi: {e}")
        return False

# Hướng dẫn cho người dùng: 
# Bước này yêu cầu bạn có 1 file Excel tổng hợp các trang PDF đã OCR. 
# Bạn hãy báo "OK" sau khi đã chạy script này thành công trên máy.
