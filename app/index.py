from flask import render_template, redirect, request, flash, url_for
from flask_dance.contrib.google import google
from flask_login import login_user, logout_user, current_user

from app import app, login_manager, db
from app.models import User, Role
from app.dao.user_dao import add_customer, add_organizer, existence_check
from app.dao import user_dao, events_dao



@app.route("/")
def index():
    artists = events_dao.get_all_artists()
    cities = events_dao.get_all_locations()
    event_types = events_dao.get_all_event_types()

    page = request.args.get("page", 1, type=int)
    pagination = events_dao.get_all_events(page=page, per_page=3)
    events = pagination.items
    return render_template("index.html", artists=artists, cities=cities, events=events, pagination=pagination, event_types=event_types)

@app.route('/search')
def search():
    artists = events_dao.get_all_artists()
    cities = events_dao.get_all_locations()
    event_types = events_dao.get_all_event_types()

    event_type_id = request.args.get("event_type_id", type=int)
    city_id = request.args.get("city_id", type=int)
    artist_id = request.args.get("artist_id", type=int)
    kw = request.args.get("kw", type=str)

    page = request.args.get("page", 1, type=int)
    pagination = events_dao.get_all_events(page=page, per_page=3, event_type_id=event_type_id, city_id=city_id,
                                           artist_id=artist_id, kw=kw)

    events = pagination.items
    return render_template("events.html", artists=artists, cities=cities, events=events, pagination=pagination,
                           event_types=event_types,selected_event_type=event_type_id,
    selected_artist=artist_id,
    selected_city=city_id,
    kw=kw)

@app.route('/login', methods=['GET', 'POST'])
def login():
    err_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = user_dao.auth_user(username, password)

        if user:
            login_user(user)

            # Nếu có next thì ưu tiên redirect về next
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            # Ngược lại dùng role để điều hướng
            if user.role == Role.ADMIN:
                return redirect('/admin')
            elif user.role == Role.CUSTOMER:
                return redirect('/')
            elif user.role == Role.ORGANIZER:
                return redirect('/organizer')
            else:
                return redirect('/login')
        else:
            err_message = 'Username or password is incorrect'

    return render_template('login.html', err_message=err_message)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    role = request.args.get('role', 'CUSTOMER')
    error_message = {}

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')


        if user_dao.existence_check(User, 'username', username):
            error_message['err_username'] = 'Username đã tồn tại'

        if password != confirm_password:
            error_message['err_password'] = 'Password và confirm password không khớp'

        if '@' not in email:
            error_message['err_email'] = 'Gmail không hợp lệ'
        elif user_dao.existence_check(User, 'email', email):
            error_message['err_email'] = 'Gmail đã tồn tại'

        if len(phone) < 10 or len(phone) > 11:
            error_message['err_phone'] = 'Số điện thoại hợp lệ từ 10-11 số'
        elif user_dao.existence_check(User, 'phone', phone):
            error_message['err_phone'] = 'Số điện thoại đã tồn tại'

        if error_message:
            flash("Đăng ký không thành công, vui lòng kiểm tra lại thông tin!", "danger")
            return render_template(
                'create_account.html',
                error_message=error_message,
                username=username,
                email=email,
                phone=phone,
                role=role
            )

        # nếu hợp lệ → xử lý theo role
        if role == "CUSTOMER":
            user = user_dao.add_customer(
                username=username,
                password=password,
                email=email,
                phone=phone,
            )
            flash(f"Welcome {username}, registered successfully as CUSTOMER!", "success")

        elif role == "ORGANIZER":
            company_name = request.form.get('company_name')
            tax_code = request.form.get('tax_code')

            user, organizer = user_dao.add_organizer(
                username=username,
                password=password,
                email=email,
                phone=phone,
                company_name=company_name,
                tax_code=tax_code
            )
            flash(f"Welcome {username}, registered successfully as ORGANIZER!", "success")

        return redirect('/login')

    return render_template('create_account.html', role=role)

@app.route('/register', methods=['GET', 'POST'])
def register():
    err_message = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')

        # Check if user already exists
        if existence_check(username=username, email=email, phone=phone):
            err_message = "Username, email, or phone number already exists"
        else:
            # Register as customer
            if role == 'customer':
                if add_customer(username=username, password=password, email=email, phone=phone):
                    flash("Registration successful! Please login.", "success")
                    return redirect(url_for('login'))
                else:
                    err_message = "Registration failed. Please try again."
            # Register as organizer
            elif role == 'organizer':
                company_name = request.form.get('company_name')
                tax_code = request.form.get('tax_code')
                if add_organizer(username=username, password=password, email=email, phone=phone,
                               company_name=company_name, tax_code=tax_code):
                    flash("Registration successful! Your organizer account is pending approval.", "success")
                    return redirect(url_for('login'))
                else:
                    err_message = "Registration failed. Please try again."

    return render_template('create_account.html', err_message=err_message)

@app.route('/event/<int:event_id>')
def detail_event():
    return render_template('index.html')

@app.route("/login/google")
def login_google():
    # Nếu chưa authorize với Google → redirect sang Google login
    if not google.authorized:
        return redirect(url_for("google.login"))
    # Nếu đã authorize, chỉ redirect tới callback để xử lý user
    return redirect(url_for("callback"))


@app.route("/callback")
def callback():
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Đăng nhập Google thất bại!", 400

    user_info = resp.json()
    email = user_info["email"]

    # Kiểm tra user trong DB
    user = user_dao.get_user_by_email(email)
    if not user:
        # Nếu chưa có, gọi hàm bên dao để tạo user
        user = user_dao.create_user_from_google(user_info)
    login_user(user)
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run(debug=True)