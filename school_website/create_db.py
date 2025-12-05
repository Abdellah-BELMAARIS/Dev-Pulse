import os
import sqlite3
from market import app, db, Item, User
from werkzeug.security import generate_password_hash
from item_stock import services_data

db_path = os.path.join(os.path.dirname(__file__), 'market.db')

print(f"Database path: {db_path}")

# Always delete existing database if it exists
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    except PermissionError:
        print("ERROR: Cannot remove database file. Please:")
        print("1. Stop the Flask app (Ctrl+C)")
        print("2. Manually delete the file: market.db")
        print("3. Run this script again")
        exit(1)

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

    added_count = 0
    for service_item in services_data:
        existing = Item.query.filter_by(service=service_item.service).first()
        if not existing:
            db.session.add(service_item)
            added_count += 1

    db.session.commit()

    print(f"Database initialization complete!")
    print(f"Added {added_count} new services")
    print(f"Sample user: username='testuser', password='password123'")