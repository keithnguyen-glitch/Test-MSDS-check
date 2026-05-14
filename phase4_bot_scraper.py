import requests
from bs4 import BeautifulSoup
import time
import json
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def crawl_moit_chemical_news():
    """
    Script giả lập crawler truy cập trang web của Cục Hóa chất hoặc Bộ Công Thương
    để tìm kiếm các văn bản pháp quy mới về quản lý hóa chất.
    """
    # Lưu ý: URL này có thể thay đổi tùy thuộc vào cổng thông tin thực tế
    # Ví dụ: https://chemicaldata.gov.vn/ hoặc cổng TTĐT Bộ Công Thương
    target_url = "https://moit.gov.vn/van-ban-phap-quy" 
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    try:
        logging.info(f"Đang truy cập: {target_url}")
        response = requests.get(target_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # HƯỚNG DẪN CẤU TRÚC HTML CHO BẠN:
            # Để lấy cấu trúc HTML thực tế của trang web:
            # 1. Mở trang web đích (vd: chemicaldata.gov.vn) bằng trình duyệt Chrome.
            # 2. Nhấn phím F12 (hoặc Chuột phải -> Inspect / Kiểm tra).
            # 3. Sử dụng công cụ "Select an element" (Mũi tên ở góc trên bên trái cửa sổ F12) 
            #    để click vào tiêu đề văn bản bạn muốn lấy rà soát.
            # 4. Xác định thẻ HTML đang bọc nó (ví dụ: <div class="news-item">, <a class="title-link">).
            # 5. Thay thế các class đó vào dòng code dưới đây.
            
            # Dưới đây là code giả định class là 'article-list' và thẻ 'a'
            articles = soup.find_all('a', class_='title-link') # TODO: Thay class thực tế vào đây
            
            new_regulations = []
            for article in articles[:10]: # Kiểm tra 10 bài mới nhất
                title = article.get_text(strip=True)
                link = article.get('href')
                if link and not link.startswith('http'):
                    link = 'https://moit.gov.vn' + link
                    
                # Chỉ lọc các văn bản có từ khóa liên quan đến hóa chất
                keywords = ['hóa chất', 'nghị định', 'thông tư', 'tiền chất', 'cấm', 'hạn chế', 'sds', 'msds']
                if any(kw in title.lower() for kw in keywords):
                    new_regulations.append({'title': title, 'link': link, 'date': time.strftime("%d/%m/%Y")})
            
            if new_regulations:
                logging.info(f"Đã phát hiện {len(new_regulations)} văn bản mới!")
                with open('cap_nhat_phap_luat.json', 'w', encoding='utf-8') as f:
                    json.dump(new_regulations, f, ensure_ascii=False, indent=4)
                
                # Tại đây có thể code thêm tính năng: Gửi email cảnh báo, bắn thông báo Telegram/Zalo, v.v.
            else:
                logging.info("Không có văn bản pháp luật mới nào về hóa chất hôm nay.")
                
        else:
            logging.error(f"Không thể truy cập trang web. Mã lỗi HTTP: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Lỗi mạng/Kết nối: {e}")

if __name__ == "__main__":
    print("Khởi động Bot cào dữ liệu tự động (Web Scraper)...")
    while True:
        crawl_moit_chemical_news()
        # Chạy vòng lặp tự động mỗi 24 giờ (86400 giây)
        logging.info("Đang ngủ đông... Sẽ tự động thức dậy kiểm tra lại sau 24 giờ.")
        time.sleep(86400) 
