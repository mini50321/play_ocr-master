import pymysql
from config import Config

def find_actor_in_database(actor_name="Aja Barrows"):
    try:
        conn = pymysql.connect(
            host=Config.JOOMLA_DB_HOST,
            user=Config.JOOMLA_DB_USER,
            password=Config.JOOMLA_DB_PASSWORD,
            database=Config.JOOMLA_DB_NAME,
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        print(f"Searching for '{actor_name}' in Joomla database...")
        print("=" * 60)
        
        cursor.execute("SHOW TABLES LIKE 'wa8wx_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\nFound {len(tables)} tables. Searching for '{actor_name}'...\n")
        
        search_term = actor_name.lower()
        found_in = []
        
        for table in tables:
            try:
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                columns = [col[0] for col in cursor.fetchall()]
                
                text_columns = []
                for col in columns:
                    col_lower = col.lower()
                    if any(keyword in col_lower for keyword in ['name', 'title', 'text', 'content', 'description']):
                        text_columns.append(col)
                
                if text_columns:
                    for col in text_columns:
                        try:
                            query = f"SELECT id, {col} FROM {table} WHERE LOWER({col}) LIKE %s LIMIT 5"
                            cursor.execute(query, (f"%{search_term}%",))
                            rows = cursor.fetchall()
                            
                            if rows:
                                found_in.append({
                                    'table': table,
                                    'column': col,
                                    'rows': rows
                                })
                                print(f"✓ Found in {table}.{col}:")
                                for row in rows:
                                    print(f"  - ID: {row[0]}, Value: {row[1][:100]}")
                                print()
                        except Exception as e:
                            pass
            except Exception as e:
                pass
        
        if not found_in:
            print(f"✗ '{actor_name}' not found in any table")
        else:
            print(f"\n✓ Found in {len(found_in)} location(s)")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_actor_in_database()

