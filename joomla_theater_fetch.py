import pymysql
from config import Config

def get_theater_from_joomla(joomla_id):
    """
    Fetch theater data directly from Joomla database by joomla_id.
    Returns dict with theater data or None if not found.
    """
    if not joomla_id:
        return None
    
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
            short_desc_col = None
            addr_col = None
            img_col = None
            
            for col in columns:
                col_lower = col.lower()
                if col_lower == 'description':
                    desc_col = col
                elif col_lower == 'short_description':
                    short_desc_col = col
                elif 'description' in col_lower or 'desc' in col_lower:
                    if 'short' not in col_lower and not desc_col:
                        desc_col = col
                    elif 'short' in col_lower and not short_desc_col:
                        short_desc_col = col
                if 'address' in col_lower or 'addr' in col_lower:
                    addr_col = col
                if 'image' in col_lower or 'logo' in col_lower or 'picture' in col_lower:
                    img_col = col
            
            select_cols = ["id", "name", "latitude", "longitude", "city", "county"]
            if desc_col:
                select_cols.append(desc_col)
            if short_desc_col and short_desc_col != desc_col:
                select_cols.append(short_desc_col)
            if addr_col:
                select_cols.append(addr_col)
            if img_col:
                select_cols.append(img_col)
            
            query = f"SELECT {', '.join(select_cols)} FROM {Config.JOOMLA_THEATER_TABLE} WHERE id = %s"
            cursor.execute(query, (joomla_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return None
            
            joomla_id_val = row[0]
            name = row[1] if len(row) > 1 else None
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
                if description:
                    description = str(description).strip()
                    if len(description) == 0:
                        description = None
                idx += 1
            
            if not description and short_desc_col and short_desc_col != desc_col:
                if len(row) > idx:
                    short_desc = row[idx]
                    if short_desc:
                        short_desc = str(short_desc).strip()
                        if len(short_desc) > 0:
                            description = short_desc
                    idx += 1
            
            if addr_col and len(row) > idx:
                address = row[idx]
                idx += 1
            if img_col and len(row) > idx:
                image = row[idx]
            
            conn.close()
            
            return {
                'joomla_id': joomla_id_val,
                'name': name,
                'latitude': latitude,
                'longitude': longitude,
                'city': city,
                'state': state,
                'description': description,
                'address': address,
                'image': image
            }
            
        except Exception as e:
            conn.close()
            print(f"Error fetching theater from Joomla: {e}")
            return None
            
    except Exception as e:
        print(f"Error connecting to Joomla database: {e}")
        return None

