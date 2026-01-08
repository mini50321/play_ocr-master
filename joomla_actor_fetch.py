import pymysql
import os
from config import Config

def get_actor_from_joomla(joomla_id):
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
            actor_table = Config.JOOMLA_ACTOR_TABLE
            cursor.execute(f"SHOW COLUMNS FROM {actor_table}")
            columns = [col[0] for col in cursor.fetchall()]
            
            photo_col = None
            name_col = None
            
            for col in columns:
                col_lower = col.lower()
                if 'photo' in col_lower or 'image' in col_lower or 'picture' in col_lower or 'avatar' in col_lower:
                    photo_col = col
                if col_lower == 'name' or col_lower == 'title':
                    name_col = col
            
            select_cols = ["id"]
            if name_col:
                select_cols.append(name_col)
            if photo_col:
                select_cols.append(photo_col)
            
            query = f"SELECT {', '.join(select_cols)} FROM {actor_table} WHERE id = %s"
            cursor.execute(query, (joomla_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return None
            
            joomla_id_val = row[0]
            name = row[1] if len(row) > 1 and name_col else None
            photo = None
            
            if photo_col:
                photo_idx = 1
                if name_col:
                    photo_idx = 2
                if len(row) > photo_idx:
                    photo = row[photo_idx]
            
            conn.close()
            
            return {
                'joomla_id': joomla_id_val,
                'name': name,
                'photo': photo
            }
            
        except Exception as e:
            conn.close()
            print(f"Error fetching actor from Joomla: {e}")
            return None
            
    except Exception as e:
        print(f"Error connecting to Joomla database: {e}")
        return None

