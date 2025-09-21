# QLDA_EventTicketingWebsite
📖 Hướng dẫn cài đặt & chạy project

🔧 Yêu cầu môi trường
Để chạy được project, cần chuẩn bị:
- Python 3.11+ 
- PyCharm IDE (hoặc IDE khác có hỗ trợ Python, nhưng khuyên dùng PyCharm)  
- MySQL 8.0+ 

1. Clone project từ GitHub
- Mở Command Prompt (CMD) hoặc Git Bash.
- Chạy lệnh sau để clone project về máy:
```bash
git clone  https://github.com/trqhuong/QLDA_EventTicketingWebsite.git
```
- Sau khi clone xong, mở project đó bằng PyCharm.
2. Tạo môi trường ảo (Virtual Environment)
- Trong PyCharm, mở Terminal ở thư mục project.
- Tạo môi trường ảo: 
```bash
python -m venv .venv 
```
- Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```
3. Tạo cơ sở dữ liệu MySQL
- Tạo database mới tên ticketsaledb trong mySQL
4. Cấu hình kết nối MySQL trong project
Mở file app/__init__.py.
Tìm dòng cấu hình MySQL URI :
```bash
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/ticketsaledb?charset=utf8mb4" % quote('password')
```
👉 Thay <password> bằng mật khẩu MySQL của bạn.

5. Khởi tạo dữ liệu ban đầu
- Chạy file models.py
6. Chạy project
- Chạy file index.py
