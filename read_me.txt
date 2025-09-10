Bước 1: Mở terminal trong thư mục dự án
Bước 2: Chạy lệnh py -3.10 -m venv .env (tùy thuộc vào version hiện tại, có thể khác 3.10)
Bước 3: Chạy lệnh Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
Bước 4: Chạy lệnh .env\Scripts\Activate.ps1
Bước 5: Chạy lệnh pip install -r requirements_voice.txt
Bước 6: Chạy lệnh streamlit run app.py. Ứng dụng sẽ chạy ở cổng http://localhost:8502/
Bước 7: Đăng nhập https://aistudio.google.com/app/apikey để tạo API key
Bước 8: Coppy và dán key vừa mới tạo vào trang http://localhost:8502/
