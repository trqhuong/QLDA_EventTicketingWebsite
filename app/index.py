from flask import render_template, redirect

from app import app, login_manager, db
from app.models import User
from flask_login import logout_user



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


if __name__ == '__main__':
    app.run(debug=True)