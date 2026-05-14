import pandas as pd
import re
import json

def clean_cas(cas_string):
    """Làm sạch mã CAS: xóa khoảng trắng, ký tự lạ."""
    if pd.isna(cas_string) or str(cas_string).strip() == "":
        return None
    # Chỉ giữ lại số và dấu gạch ngang
    cleaned = re.sub(r'[^0-9-]', '', str(cas_string))
    return cleaned.strip()

def process_chemical_data(file_path):
    print(f"Đang đọc dữ liệu từ: {file_path}...")
    
    # Giả định tệp đầu vào là Excel có các cột: STT, TenVN, TenEN, CAS, HS, PhapLy
    # Nếu bạn dùng bản OCR từ PDF, chúng ta sẽ cần script bóc tách phức tạp hơn.
    try:
        df = pd.read_excel(file_path)
        
        # 1. Làm sạch dữ liệu
        df['Mã CAS'] = df['Mã CAS'].apply(clean_cas)
        df['Tên hóa chất (Tiếng Việt)'] = df['Tên hóa chất (Tiếng Việt)'].str.strip()
        
        # 2. Xử lý phân loại sơ bộ (Dựa trên cột Căn cứ pháp lý)
        def classify(row):
            legal = str(row.get('Căn cứ pháp lý', '')).lower()
            if 'cấm' in legal:
                return 'BANNED'
            elif 'tiền chất' in legal:
                return 'PRECURSOR'
            elif 'khai báo' in legal:
                return 'DECLARATION'
            return 'NORMAL'

        df['Phân loại'] = df.apply(classify, axis=1)

        # 3. Xuất ra file database.json để dùng cho các bước sau
        database = df.to_dict(orient='records')
        with open('database.json', 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=4)
            
        print(f"Thành công! Đã tạo file database.json với {len(database)} chất.")
        return True
    except Exception as e:
        print(f"Lỗi khi xử lý file: {e}")
        return False

# Lưu ý: Thay tên file 'danh_sach_2105_chat.xlsx' bằng tên file bạn đang có
# process_chemical_data('danh_sach_2105_chat.xlsx')
