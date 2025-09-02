import os
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
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/ticketsaledb?charset=utf8mb4" % quote('123456')
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
