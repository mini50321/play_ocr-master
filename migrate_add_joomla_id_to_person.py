from app import app, db
from models import Person
from sqlalchemy import text, inspect
from config import Config

def migrate_add_joomla_id():
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('person')]
            
            if 'joomla_id' not in columns:
                print("Adding joomla_id column to person table...")
                
                if Config.DB_TYPE == 'mysql':
                    db.session.execute(text("ALTER TABLE person ADD COLUMN joomla_id INTEGER NULL"))
                else:
                    db.session.execute(text("ALTER TABLE person ADD COLUMN joomla_id INTEGER"))
                
                db.session.commit()
                print("✓ Successfully added joomla_id column to person table")
            else:
                print("✓ joomla_id column already exists in person table")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    migrate_add_joomla_id()

