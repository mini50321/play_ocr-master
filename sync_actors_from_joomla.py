from app import app, db
from models import Person
from joomla_actor_fetch import get_actor_from_joomla
import pymysql
from config import Config

def normalize_name_for_matching(name):
    if not name:
        return ""
    name = name.strip().lower()
    name = ' '.join(name.split())
    return name

def find_joomla_actor_by_name(name):
    if not name or len(name.strip()) < 3:
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
            normalized_search = normalize_name_for_matching(name)
            name_parts = normalized_search.split()
            
            if len(name_parts) < 2:
                conn.close()
                return None
            
            search_variations = [normalized_search]
            if len(name_parts) >= 2:
                first_last = f"{name_parts[0]} {name_parts[-1]}"
                search_variations.append(first_last)
                if name_parts[0] == 'aja':
                    search_variations.append(f"aeja {name_parts[-1]}")
                elif name_parts[0] == 'aeja':
                    search_variations.append(f"aja {name_parts[-1]}")
            
            try:
                actor_table = Config.JOOMLA_ACTOR_TABLE
                cursor.execute(f"SHOW COLUMNS FROM {actor_table}")
                columns = [col[0] for col in cursor.fetchall()]
                
                name_col = None
                for col in columns:
                    col_lower = col.lower()
                    if col_lower == 'name' or col_lower == 'title':
                        name_col = col
                        break
                
                if name_col:
                    for search_term in search_variations:
                        query = f"SELECT id, {name_col} FROM {actor_table} WHERE LOWER(TRIM({name_col})) = %s AND state = 1 LIMIT 1"
                        cursor.execute(query, (search_term,))
                        row = cursor.fetchone()
                        
                        if row:
                            joomla_id = row[0]
                            joomla_name = row[1]
                            conn.close()
                            return {'id': joomla_id, 'name': joomla_name}
            except Exception:
                pass
            
            for search_term in search_variations:
                query = "SELECT id, title FROM wa8wx_content WHERE LOWER(TRIM(title)) = %s AND state = 1 LIMIT 1"
                cursor.execute(query, (search_term,))
                row = cursor.fetchone()
                
                if row:
                    joomla_id = row[0]
                    joomla_name = row[1]
                    if search_term in normalize_name_for_matching(joomla_name):
                        conn.close()
                        return {'id': joomla_id, 'name': joomla_name}
            
            for search_term in search_variations:
                query = "SELECT id, title FROM wa8wx_content WHERE (LOWER(introtext) LIKE %s OR LOWER(fulltext) LIKE %s) AND state = 1 LIMIT 1"
                pattern = f"%{search_term}%"
                cursor.execute(query, (pattern, pattern))
                row = cursor.fetchone()
                
                if row:
                    joomla_id = row[0]
                    joomla_name = row[1]
                    conn.close()
                    return {'id': joomla_id, 'name': joomla_name, 'found_in_content': True}
            
            for search_term in search_variations:
                query = "SELECT id, title FROM wa8wx_tags WHERE LOWER(TRIM(title)) = %s AND published = 1 LIMIT 1"
                cursor.execute(query, (search_term,))
                row = cursor.fetchone()
                
                if row:
                    joomla_id = row[0]
                    joomla_name = row[1]
                    conn.close()
                    return {'id': joomla_id, 'name': joomla_name}
            
            conn.close()
            return None
            
        except Exception as e:
            conn.close()
            print(f"Error searching for actor in Joomla: {e}")
            return None
            
    except Exception as e:
        print(f"Error connecting to Joomla database: {e}")
        return None

def sync_actors_from_joomla():
    with app.app_context():
        persons = Person.query.all()
        matched = 0
        not_found = 0
        already_linked = 0
        
        print(f"Found {len(persons)} Person records to check...")
        print("=" * 60)
        
        for person in persons:
            if person.joomla_id:
                already_linked += 1
                print(f"✓ {person.name} (ID: {person.id}) - Already linked to Joomla ID: {person.joomla_id}")
                continue
            
            joomla_actor = find_joomla_actor_by_name(person.name)
            
            if joomla_actor:
                person.joomla_id = joomla_actor['id']
                matched += 1
                print(f"✓ {person.name} (ID: {person.id}) - Matched to Joomla ID: {joomla_actor['id']} ({joomla_actor['name']})")
            else:
                not_found += 1
                print(f"✗ {person.name} (ID: {person.id}) - No match found in Joomla")
        
        try:
            db.session.commit()
            print("=" * 60)
            print(f"Sync complete!")
            print(f"  - Matched and linked: {matched}")
            print(f"  - Already linked: {already_linked}")
            print(f"  - Not found in Joomla: {not_found}")
            print(f"  - Total processed: {len(persons)}")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing changes: {e}")
            raise

if __name__ == "__main__":
    sync_actors_from_joomla()

