from flask import render_template, redirect

from app import app, login_manager, db
from app.models import User
from flask_login import logout_user
from flask import Flask, render_template, request, redirect, url_for, session, flash, sessions, jsonify
from flask.cli import load_dotenv

from app import app, login_manager, db, utils
from app.dao import user_dao, events_dao, ticket_dao
from app.models import User, Role
from flask_login import login_user, logout_user, login_required, current_user
from flask_dance.contrib.google import make_google_blueprint, google


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    return render_template('create_account.html')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/events/<category>")
def events_by_category(category):
    events = events_dao.get_events_by_category(category)
    return render_template("events.html", events=events, category=category)


@app.route('/detail_event')
def detail_event():
    cart = session.get(app.config['CART_KEY'], {})
    cart_info = utils.cart_stats(cart)

    event_id = request.args.get('event_id')

    event_details = events_dao.get_details_by_event_id(event_id)
    tickets = ticket_dao.get_tickets_by_event_id(event_id)

    return render_template('detail_event.html', event=event_details, event_id=event_id, tickets=tickets,
                           cart_info=cart_info)


@app.route("/api/cart", methods=['post'])
def add_to_cart():
    key = app.config['CART_KEY']

    data = request.json
    if not data or 'ticket_id' not in data or 'event_name' not in data or 'type' not in data or 'price' not in data:
        return jsonify({'error': 'Missing data in request'}), 400
    id = str(data['ticket_id'])
    event_name = str(data['event_name'])
    type = str(data['type'])
    price = data['price']
    cart = session[key] if key in session else {}
    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {
            "ticket_id": id,
            "event_name": event_name,
            "type": type,
            "price": price,
            "quantity": 1
        }


    session[key] = cart

    return jsonify(utils.cart_stats(cart))
@app.route("/api/cart", methods=['put'])
def remove_from_cart():
    key = app.config['CART_KEY']

    data = request.json
    if not data or 'ticket_id' not in data:
        return jsonify({'error': 'Missing data in request'}), 400
    id = str(data['ticket_id'])
    cart = session.get(key, {})
    if id in cart:
        cart[id]['quantity'] -= 1
        if(cart[id]['quantity'] <= 0):
            del cart[id]



    session[key] = cart

    return jsonify(utils.cart_stats(cart))

@app.route('/book_ticket')
def book_ticket():
    return render_template('book_ticket.html')


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
