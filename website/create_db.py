python
import os
import sys

sys.path.append(os.path.dirname(__file__))

from market import app, db
from market.models import Item, User
from werkzeug.security import generate_password_hash
db_path = os.path.join(os.path.dirname(__file__), 'market.db')

print(f"Database path: {db_path}")

def is_valid_sqlite_db(path):
    if not os.path.exists(path):
        return False

    try:
        with open(path, 'rb') as f:
            header = f.read(100)
            return header.startswith(b'SQLite format 3\000')
    except:
        return False


if os.path.exists(db_path):
    if not is_valid_sqlite_db(db_path):
        print("Warning: Existing database file appears corrupted or invalid")
        try:
            os.remove(db_path)
            print("Removed corrupted database file")
        except PermissionError:
            print("ERROR: Cannot remove database file. Please:")
            print("1. Stop the Flask app (Ctrl+C)")
            print("2. Manually delete the file: market.db")
            print("3. Run this script again")
            exit(1)
    else:
        print("Valid database file found")

with app.app_context():
    print("Creating database tables...")
    db.create_all()

    from sqlalchemy import inspect

    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables created: {tables}")

    existing_user = User.query.filter_by(username="testuser").first()
    if not existing_user:
        sample_user = User(
            username="testuser",
            email="test@example.com",
            password=generate_password_hash("password123")
        )
        db.session.add(sample_user)
        print("Created sample user")
    else:
        print("Sample user already exists")

    services_data = [
        {
            'service': 1,
            'name': "Web Development Course",
            'price': 50,
            'hours': 60,
            'barcode': "123456789012",
            'description': "Full-stack web development course using modern technologies",
            'instructor': "Abdellah BELMAARIS"
        },
        {
            'service': 2,
            'name': "Mobile App Development Course",
            'price': 700,
            'hours': 67,
            'barcode': "234567890123",
            'description': "iOS and Android app development course with native or cross-platform solutions",
            'instructor': "Abdelahamid BELMAARIS"
        },
        {
            'service': 3,
            'name': "Web Development Course",
            'price': 450,
            'hours': 35,
            'barcode': "345678901234",
            'description': "Web development course covering modern design principles and best practices.",
            'instructor': "Hajar BELMAARIS"
        },
        {
            'service' : 4,
            'name' : "REVIT Architecture Course",
            'price' : 100,
            'hours' : 70,
            'barcode' : "456789012345",
            'description' : "REVIT software training course for architecture, modeling, and structural design.",
            'instructor' : "Amina ELASRI"
        },
    ]
    added_count = 0
    for service_info in services_data:
        existing = Item.query.filter_by(service=service_info['service']).first()
        if not existing:
            service = Item(**service_info)
            db.session.add(service)
            added_count += 1

    db.session.commit()

    print(f"Database initialization complete!")
    print(f"Added {added_count} new services")
    print(f"Sample user: username='testuser', password='password123'")