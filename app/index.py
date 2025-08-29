
from flask import render_template, redirect

from app import app, login_manager, db
from app.models import User
from flask_login import logout_user
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask.cli import load_dotenv

from app import app, login_manager, db
from app.dao import user_dao,events_dao
from app.models import User,Role
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
    event_id = request.args.get('event_id')

    sample_events = {
        "1": {
            "name": "Đêm nhạc Acoustic",
            "time": "18:00",
            "formatted_date": "15/08/2025",
            "description": "Quá là đẹp",
            "location": "Hà Nội",
            "price": "100,000 VND",
            "image": "images/1.jpg"
        },
        "2": {
            "name": "Hội chợ Sách",
            "date": "2025-09-01",
            "formatted_date": "01/09/2025",
            "location": "TP.HCM",
            "price": "Miễn phí",
            "image": "images/2.jpg"
        }
    }

    event = sample_events.get(event_id)

    if not event:
        return "Sự kiện không tồn tại", 404

    return render_template('detail_event.html', event=event, event_id=event_id)

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