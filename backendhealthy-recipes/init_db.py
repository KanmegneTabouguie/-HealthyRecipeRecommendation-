from main import db
from main import app

# Create the database and the tables
with app.app_context():
    db.create_all()
    print("Database and tables created")
