from app import app, login_manager, db
from app.models import User, Role, TypeTicket
from app.dao.user_dao import add_customer, add_organizer, existence_check
import cloudinary.uploader
import locale

from flask import Flask, render_template, request, redirect, url_for, session, flash, sessions, jsonify
from flask.cli import load_dotenv

from datetime import datetime
from app import app, login_manager, db, utils, VNPAY_CONFIG
from app.dao import user_dao, events_dao, ticket_dao, vnpay_dao, bill_dao
from app.models import User, Role

from flask_login import login_user, logout_user, login_required, current_user
from flask_dance.contrib.google import make_google_blueprint, google



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



@app.route("/organizer")
def organizer():
    cities = events_dao.get_all_locations()
    event_types = events_dao.get_all_event_types()
    return render_template("organizer.html", cities=cities, event_types=event_types)

@app.route("/api/districts/<int:city_id>")
def get_districts_by_city(city_id):
    """API endpoint để lấy danh sách quận/huyện theo tỉnh/thành"""
    districts = events_dao.get_districts_by_city(city_id)
    return jsonify([{"id": district.id, "name": district.name} for district in districts])


@app.route("/create_event", methods=['GET', 'POST'])
def create_event_form():
    if request.method == 'POST':
        try:
            # Lấy dữ liệu cơ bản từ form
            event_name = request.form.get('event_name')
            city_id = request.form.get('city_id')
            district_id = request.form.get('district_id')
            address = request.form.get('address')
            event_type_id = request.form.get('event_type_id')
            description = request.form.get('description')
            image_url = request.files.get('image_url')

            # Lấy thông tin thời gian
            date = request.form.get('date')
            time = request.form.get('time')

            # Lấy thông tin tickets
            ticket_names = request.form.getlist('ticket_name[]')
            ticket_prices = request.form.getlist('ticket_price[]')
            ticket_quantities = request.form.getlist('ticket_quantity[]')
            ticket_descriptions = request.form.getlist('ticket_description[]')
            ticket_types = request.form.getlist('ticket_type[]')  # Lấy ticket types từ form
            print(current_user.organizer.id)
            # Validate dữ liệu
            if not all([event_name, city_id, district_id, address, event_type_id, date, time, image_url]):
                flash("Vui lòng điền đầy đủ thông tin bắt buộc!", "error")
                return redirect(url_for('create_event_form'))

            if not ticket_names or len(ticket_names) == 0:
                flash("Vui lòng thêm ít nhất một loại vé!", "error")
                return redirect(url_for('create_event_form'))

            avatar_path = None
            if image_url:
                res = cloudinary.uploader.upload(image_url)
                avatar_path = res['secure_url']

            # Tạo sự kiện mới
            organizer_id = current_user.organizer.id if current_user.is_authenticated and hasattr(current_user,
                                                                                                  'organizer') and current_user.organizer else 1

            new_event = events_dao.create_event_with_tickets(
                name=event_name,
                city_id=int(city_id),
                district_id=int(district_id),
                address=address,
                event_type_id=int(event_type_id),
                description=description,
                image_url=avatar_path,
                date=date,
                time=time,
                organizer_id=organizer_id,
                ticket_data={
                    'names': ticket_names,
                    'prices': [float(price) for price in ticket_prices if price],
                    'quantities': [int(qty) for qty in ticket_quantities if qty],
                    'descriptions': ticket_descriptions,
                    'types': ticket_types
                }
            )

            flash("Tạo sự kiện thành công!", "success")
            return redirect(url_for('organizer'))

        except ValueError as ve:
            flash(f"Dữ liệu không hợp lệ: {str(ve)}", "error")
        except Exception as e:
            flash(f"Lỗi khi tạo sự kiện: {str(e)}", "error")
        return redirect(url_for('create_event_form'))

    # GET request - hiển thị form
    cities = events_dao.get_all_locations()
    event_types = events_dao.get_all_event_types()
    ticket_types = list(TypeTicket)
    return render_template("create_event_new.html", cities=cities, event_types=event_types, ticket_types=ticket_types)


@app.route('/detail_event')
def detail_event():
    cart = session.get(app.config['CART_KEY'], {})
    if cart:
        session.pop(app.config['CART_KEY'], None)
        cart = {}
        # for cart_id,ticket_details in cart.items():
        #     print(f"ticket_id: {cart_id}, quantity: {ticket_details['quantity']} \n")
    else :
        print("cart is empty")
    cart_info = utils.cart_stats(cart)

    event_id = request.args.get('event_id')

    event_details = events_dao.get_details_by_event_id(event_id)
    tickets = ticket_dao.get_tickets_by_event_id(event_id)
    tickets_dict = [
        {
            "id": t.id,
            "type": t.type.value,
            "price": t.price,
            "quantity": t.quantity
        }
        for t in tickets
    ]
    return render_template('detail_event.html', event=event_details, event_id=event_id, tickets=tickets,
                           tickets_dict = tickets_dict,cart_info = cart_info)


@app.route("/api/cart", methods=['post'])

def add_to_cart():
    key = app.config['CART_KEY']

    data = request.json
    if not data or 'ticket_id' not in data  or 'type' not in data or 'price' not in data:
        return jsonify({'error': 'Missing data in request'}), 400
    id = str(data['ticket_id'])
    type = str(data['type'])
    price = float(data['price'])
    cart = session[key] if key in session else {}
    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            "ticket_id": id,
            "type": type,
            "price": price,
            "quantity": 1
        }

    session[key] = cart
    return jsonify(utils.cart_stats(cart))

@app.route("/api/cart", methods=['put'])
def remove_from_cart():
    key = app.config['CART_KEY']
    # Nhận dữ liệu JSON từ FE, parse thành Python Object // Deserialize JSON -> Object(PythonObject)

    #Xử lí logic xong, parse lại thành JSON gửi về clien (Serialize) thông quan jsonify
    data = request.json
    # print(data)
    if not data or 'ticket_id' not in data:
        return jsonify({'error': 'Missing data in request'}), 400
    id = str(data['ticket_id'])
    cart = session.get(key, {})
    if id in cart:
        # print('existed')
        cart[id]['quantity'] -= 1
        if(cart[id]['quantity'] <= 0):
            del cart[id]
    else:
        # print('none existed')
        return  jsonify({'error' : 'Cannot update ticket has quantity = 0'}),400



    session[key] = cart

    return jsonify(utils.cart_stats(cart))

login_manager.login_view = '/login'
@app.route('/book_ticket')
@login_required
def book_ticket():

    key = app.config['CART_KEY']

    cart = session.get(key, None)
    total = 0
    for key in cart:
        total += cart[key]['quantity'] * cart[key]['price']
    event_id = request.args.get('event_id')

    event_details = events_dao.get_details_by_event_id(event_id)

    return render_template('book_ticket.html',cart = cart,total = total,event_details=event_details)

@app.route('/pay_via_VNPAY', methods = ["POST"])
def pay():
    if (request.method== 'POST'):

        event_id = request.form.get("eventId")
        amount_str  = request.form.get("amount")
        amount = float(amount_str)
        vnp = vnpay_dao.vnpay()
        vnp.requestData['vnp_Version'] = '2.1.0'
        # vnp.requestData['vnp_BankCode'] = 'NCB'
        vnp.requestData['vnp_Command'] = 'pay'
        # vnp.requestData['vnp_CardType'] = 'ATM'
        vnp.requestData['vnp_BankCode'] = 'NCB'
        vnp.requestData['vnp_TmnCode'] = VNPAY_CONFIG['vnp_TmnCode']
        vnp.requestData['vnp_Amount'] =  str(int(amount * 100))
        vnp.requestData['vnp_CurrCode'] = 'VND'
        vnp.requestData['vnp_TxnRef'] = f"{event_id}{datetime.now().strftime('%Y%m%d%H%M%S')}"
        vnp.requestData['vnp_OrderInfo'] = 'Thanh toan'
        vnp.requestData['vnp_OrderType'] = 'other'
        vnp.requestData['vnp_Locale'] = 'vn'
        vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
        vnp.requestData['vnp_IpAddr'] = "127.0.0.1"
        vnp.requestData['vnp_ReturnUrl'] = url_for('vnpay_return', _external=True)

        # Lấy URL thanh toán
        vnp_payment_url = vnp.get_payment_url(
            VNPAY_CONFIG['vnp_Url'],
            VNPAY_CONFIG['vnp_HashSecret']
        )

        print("Redirecting to VNPAY:", vnp_payment_url)

        return redirect(vnp_payment_url)


@app.route('/vnpay_return')
def vnpay_return():
    is_valid = vnpay_dao.verify_return(request.args, VNPAY_CONFIG['vnp_HashSecret'])
    key = app.config['CART_KEY']

    cart = session.get(key, None)
    if not is_valid:
        return "Sai chữ ký, giao dịch không hợp lệ", 400

    vnp_response_code = request.args.get("vnp_ResponseCode")
    txn_status = request.args.get("vnp_TransactionStatus")

    if vnp_response_code == "00" and txn_status == "00":
        bill = bill_dao.create_bill_bill_detail(current_user,cart)
        utils.send_invoice(current_user.email,bill,cart)
        session.pop(key, None)
        flash("Thanh toán thành công!", "success")
        return redirect(url_for("index"))
    else:
        return f"Giao dịch thất bại. Mã lỗi: {vnp_response_code}, Trạng thái: {txn_status}"

@app.route("/organizer")
def organizer_header():
    return render_template("organizer.html")


@app.route("/create_event")
def create_event():
    return render_template("create_event.html")


@app.route("/my_event")
def my_event():
    return render_template("my_event.html")


@app.route("/report_event")
def report_event():
    return render_template("report_event.html")


@app.route("/my_ticket")
def my_ticket():
    return render_template("my_ticket.html")


if __name__ == '__main__':
    app.run(debug=True)
