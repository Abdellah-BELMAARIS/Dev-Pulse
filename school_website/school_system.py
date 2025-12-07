from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (UserMixin, LoginManager, login_user, logout_user, login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'market.db')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login_page'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    barcode = db.Column(db.String(12), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructor = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'Item {self.name}'

def init_database():
    if not os.path.exists(db_path):
        print(f"Creating database at {db_path}")
        with app.app_context():
            db.create_all()
            print("Database tables created")
    else:
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()
        except sqlite3.DatabaseError:
            print(f"WARNING: {db_path} is not a valid SQLite database")
            os.remove(db_path)
            with app.app_context():
                db.create_all()
                print("Recreated corrupted database")

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/services')
def services_page():
    try:
        items = Item.query.all()
        return render_template('services.html', items=items)
    except Exception as e:
        print(f"Error loading services: {e}")
        return render_template('services.html', items=[])

@app.route('/item/<int:item_id>')
def item_details(item_id):
    try:
        item = Item.query.get_or_404(item_id)
        return jsonify({
            'service': item.service,
            'name': item.name,
            'price': item.price,
            'hours': item.hours,
            'barcode': item.barcode,
            'description': item.description,
            'instructor': item.instructor
        })
    except:
        return jsonify({'error': 'Item not found'}), 404

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get("username")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if password1 != password2:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register_page'))

        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash("Username already exists!", "danger")
            return redirect(url_for('register_page'))

        if email_exists:
            flash("Email already registered!", "danger")
            return redirect(url_for('register_page'))

        hashed_pw = generate_password_hash(password1)
        user = User(username=username, email=email, password=hashed_pw)

        try:
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully!", "success")
            return redirect(url_for('login_page'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {str(e)}", "danger")
            return redirect(url_for('register_page'))

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get("username")
        password_input = request.form.get("password")
        try:
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password_input):
                login_user(user)
                flash("Logged in successfully!", "success")
                return redirect(url_for("dashboard_page"))
            else:
                flash("Incorrect username or password", "danger")
        except Exception as e:
            flash(f"Database error: {str(e)}", "danger")
            return redirect(url_for('login_page'))
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash("Logged out!", "info")
    return redirect(url_for("home_page"))

@app.route('/dashboard')
@login_required
def dashboard_page():
    return render_template("dashboard.html")

@app.route('/cart')
@login_required
def cart_page():
    return render_template("cart.html")

if __name__ == '__main__':
    init_database()

    print(f"Starting Flask app...")
    print(f"Database: {db_path}")
    print(f"Home page: http://127.0.0.1:5000")
    app.run(debug=True)
