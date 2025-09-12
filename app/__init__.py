import os

import cloudinary
from dotenv import load_dotenv

# Cho phép sử dụng HTTP (chỉ dùng khi phát triển local, không dùng cho production!)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask
from urllib.parse import quote
from flask_dance.contrib.google import make_google_blueprint
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE= True # nếu chạy HTTPS
)

load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/ticketsaledb?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['CART_KEY'] = 'cart'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# --- cấu hình đăng nhập Google ---

google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret= os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_to="callback"   # sau khi login xong sẽ về hàm index
)
app.register_blueprint(google_bp, url_prefix="/login")


VNPAY_CONFIG = {
    'vnp_TmnCode': 'K1L8ILZ3',
    'vnp_HashSecret': 'EHGJSI2HPHG4UNUNVLX30ZGEQ4K8KLXQ',
    'vnp_Url': 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html',
    "vnp_ReturnUrl": "http://localhost:5000/"
}


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hintran6@gmail.com'       # email gửi
app.config['MAIL_PASSWORD'] = 'yqzcliefayiqbaov'
app.config['MAIL_DEFAULT_SENDER'] = ('Event Ticketing', 'hintran6@gmail.com')



cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

