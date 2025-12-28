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
            try:
                cursor.execute(f"SHOW COLUMNS FROM {Config.JOOMLA_THEATER_TABLE}")
                columns = [col[0] for col in cursor.fetchall()]
                
                desc_col = None
                addr_col = None
                img_col = None
                
                for col in columns:
                    col_lower = col.lower()
                    if 'description' in col_lower or 'desc' in col_lower:
                        desc_col = col
                    if 'address' in col_lower or 'addr' in col_lower:
                        addr_col = col
                    if 'image' in col_lower or 'logo' in col_lower or 'picture' in col_lower:
                        img_col = col
                
                select_cols = ["id", "name", "latitude", "longitude", "city", "county"]
                if desc_col:
                    select_cols.append(desc_col)
                if addr_col:
                    select_cols.append(addr_col)
                if img_col:
                    select_cols.append(img_col)
                
                query = f"SELECT {', '.join(select_cols)} FROM {Config.JOOMLA_THEATER_TABLE} WHERE state = 1"
                cursor.execute(query)
                joomla_theaters = cursor.fetchall()
            except Exception as e:
                print(f"Error detecting columns, using basic query: {e}")
                cursor.execute(f"SELECT id, name, latitude, longitude, city, county FROM {Config.JOOMLA_THEATER_TABLE} WHERE state = 1")
                joomla_theaters = cursor.fetchall()
                desc_col = None
                addr_col = None
                img_col = None
            
            synced_count = 0
            for row in joomla_theaters:
                joomla_id = row[0]
                joomla_name = row[1]
                latitude = row[2] if len(row) > 2 else None
                longitude = row[3] if len(row) > 3 else None
                city = row[4] if len(row) > 4 else None
                state = row[5] if len(row) > 5 else None
                
                description = None
                address = None
                image = None
                
                idx = 6
                if desc_col and len(row) > idx:
                    description = row[idx]
                    idx += 1
                if addr_col and len(row) > idx:
                    address = row[idx]
                    idx += 1
                if img_col and len(row) > idx:
                    image = row[idx]
                
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
                    if description is not None and existing.description != description:
                        existing.description = description
                        updated = True
                    if address is not None and existing.address != address:
                        existing.address = address
                        updated = True
                    if image is not None and existing.image != image:
                        existing.image = image
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
                        if description is not None:
                            existing_by_name.description = description
                        if address is not None:
                            existing_by_name.address = address
                        if image is not None:
                            existing_by_name.image = image
                        synced_count += 1
                    else:
                        new_theater = Theater(
                            name=joomla_name, 
                            joomla_id=joomla_id,
                            latitude=latitude,
                            longitude=longitude,
                            city=city,
                            state=state,
                            description=description,
                            address=address,
                            image=image
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
