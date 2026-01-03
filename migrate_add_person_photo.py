from app import app
from models import db
from sqlalchemy import text

def migrate_add_person_photo():
    with app.app_context():
        try:
            db.session.execute(text("ALTER TABLE person ADD COLUMN photo VARCHAR(200)"))
            db.session.commit()
            print("Successfully added 'photo' column to person table")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("Column 'photo' already exists in person table")
            else:
                print(f"Error adding column: {e}")
                db.session.rollback()

if __name__ == "__main__":
    migrate_add_person_photo()

