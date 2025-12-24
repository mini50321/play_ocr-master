import pymysql
from models import db, Theater
from config import Config
from app import app

def sync_theaters_from_joomla():
    with app.app_context():
        try:
            conn = pymysql.connect(
                host=Config.JOOMLA_DB_HOST,
                user=Config.JOOMLA_DB_USER,
                password=Config.JOOMLA_DB_PASSWORD,
                database=Config.JOOMLA_DB_NAME,
                charset='utf8mb4'
            )
            
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, name, latitude, longitude, city, county FROM {Config.JOOMLA_THEATER_TABLE} WHERE state = 1")
            joomla_theaters = cursor.fetchall()
            
            synced_count = 0
            for joomla_id, joomla_name, latitude, longitude, city, state in joomla_theaters:
                existing = Theater.query.filter_by(joomla_id=joomla_id).first()
                
                if existing:
                    updated = False
                    if existing.name != joomla_name:
                        existing.name = joomla_name
                        updated = True
                    if str(existing.latitude) != str(latitude) if latitude else existing.latitude != None:
                        existing.latitude = latitude
                        updated = True
                    if str(existing.longitude) != str(longitude) if longitude else existing.longitude != None:
                        existing.longitude = longitude
                        updated = True
                    if existing.city != city:
                        existing.city = city
                        updated = True
                    if existing.state != state:
                        existing.state = state
                        updated = True
                    if updated:
                        synced_count += 1
                else:
                    existing_by_name = Theater.query.filter(
                        Theater.name.ilike(joomla_name)
                    ).first()
                    
                    if existing_by_name:
                        existing_by_name.joomla_id = joomla_id
                        existing_by_name.latitude = latitude
                        existing_by_name.longitude = longitude
                        existing_by_name.city = city
                        existing_by_name.state = state
                        synced_count += 1
                    else:
                        new_theater = Theater(
                            name=joomla_name, 
                            joomla_id=joomla_id,
                            latitude=latitude,
                            longitude=longitude,
                            city=city,
                            state=state
                        )
                        db.session.add(new_theater)
                        synced_count += 1
            
            db.session.commit()
            conn.close()
            
            print(f"Synced {synced_count} theaters from Joomla")
            return synced_count
            
        except Exception as e:
            print(f"Error syncing theaters: {e}")
            db.session.rollback()
            return 0

if __name__ == "__main__":
    sync_theaters_from_joomla()
