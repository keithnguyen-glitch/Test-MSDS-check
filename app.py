import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import json
import os

# Page config
st.set_page_config(page_title="ECUS Invoice Extractor", layout="wide")

# --- ẨN THANH MENU VÀ FOOTER MẶC ĐỊNH CỦA STREAMLIT ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("Tự động trích xuất dữ liệu Invoice/Packing List (ECUS)")

# Lấy API Key từ Environment Variable hoặc Input của người dùng
api_key = st.text_input("Nhập Google Gemini API Key của bạn:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    # Model config
    generation_config = {
      "temperature": 0.1,
      "top_p": 0.95,
      "top_k": 64,
      "max_output_tokens": 8192,
      "response_mime_type": "application/json",
    }
    
    model = genai.GenerativeModel(
      model_name="gemini-2.5-pro",
      generation_config=generation_config,
      system_instruction="""
      Bạn là một chuyên gia phân tích chứng từ xuất nhập khẩu (Hải quan Việt Nam).
      Trích xuất thông tin từ đoạn text (Invoice/Packing List) được cung cấp và trả về chuẩn JSON sau:
      {
        "thong_tin_chung": {
          "so_invoice": "",
          "ngay_invoice": "",
          "shipper": "",
          "consignee": "",
          "dieu_kien_giao_hang": "",
          "tong_tri_gia": "",
          "loai_tien_te": "",
          "tong_trong_luong_gw": ""
        },
        "danh_sach_hang": [
          {
            "ten_hang": "",
            "so_luong": "",
            "don_vi_tinh": "",
            "don_gia": "",
            "thanh_tien": "",
            "hs_code_du_doan": ""
          }
        ]
      }
      Chỉ trả về JSON hợp lệ, không kèm giải thích. Nếu không tìm thấy thông tin cho một trường, hãy để chuỗi rỗng "".
      Để nội dung dễ đọc nhất để copy sang hệ thống ECUS, loại bỏ các ký tự thừa. Đặc biệt là HS Code, hãy dựa vào mô tả hàng hoá để dự đoán mã HS 8 số áp dụng theo biểu thuế xuất nhập khẩu Việt Nam.
      """
    )

st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.header("Tải lên chứng từ (PDF)")
    uploaded_file = st.file_uploader("Chọn file Invoice / Packing List dạng PDF", type="pdf")
    
    extracted_text = ""
    
    if uploaded_file is not None:
        try:
            # Lưu file tạm để PyMuPDF đọc
            with open("temp_doc.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Khởi tạo PyMuPDF
            doc = fitz.open("temp_doc.pdf")
            for page in doc:
                extracted_text += page.get_text()
            
            st.success("Đọc text từ PDF thành công.")
            with st.expander("Xem text thô"):
                st.text(extracted_text)
                
            os.remove("temp_doc.pdf")
            
        except Exception as e:
            st.error(f"Lỗi đọc file PDF: {e}")

with col2:
    st.header("Kết quả trích xuất ECUS")
    if uploaded_file is not None and api_key and extracted_text:
        if st.button("Phân tích bằng AI (Gemini)", type="primary"):
            with st.spinner("Đang sử dụng AI phân tích chứng từ..."):
                try:
                    chat_session = model.start_chat()
                    response = chat_session.send_message(extracted_text)
                    
                    data = json.loads(response.text)
                    
                    st.subheader("Thông tin chung (Tờ khai)")
                    # Dùng Input và Button Copy
                    for key, val in data.get("thong_tin_chung", {}).items():
                        c1, c2 = st.columns([3, 1])
                        c1.text_input(key.replace("_", " ").title(), value=str(val), key=f"gen_{key}")
                    
                    st.subheader("Danh sách hàng hóa")
                    for idx, item in enumerate(data.get("danh_sach_hang", [])):
                        st.write(f"**Dòng hàng {idx + 1}**")
                        for key, val in item.items():
                            st.text_input(key.replace("_", " ").title(), value=str(val), key=f"item_{idx}_{key}")
                        st.write("---")
                        
                except Exception as e:
                    st.error(f"Lỗi khi gọi API: {e}")
    elif uploaded_file and not api_key:
        st.warning("Vui lòng nhập API Key ở phía trên để tiếp tục.")
