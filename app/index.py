from flask import Flask,render_template


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

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

@app.route("/book_ticket")
def book_ticket():
    return render_template("book_ticket.html")

if __name__ == '__main__':
    app.run(debug=True)