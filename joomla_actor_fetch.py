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
                
                if row:
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
            except Exception:
                pass
            
            query = "SELECT id, title, images, introtext, fulltext FROM wa8wx_content WHERE id = %s AND state = 1"
            cursor.execute(query, (joomla_id,))
            row = cursor.fetchone()
            
            if not row:
                query = "SELECT id, title, images FROM wa8wx_tags WHERE id = %s AND published = 1"
                cursor.execute(query, (joomla_id,))
                row = cursor.fetchone()
                
                if row:
                    joomla_id_val = row[0]
                    name = row[1] if len(row) > 1 else None
                    images_json = row[2] if len(row) > 2 else None
                    photo = None
                    
                    if images_json:
                        try:
                            import json
                            images_data = json.loads(images_json) if isinstance(images_json, str) else images_json
                            if isinstance(images_data, dict):
                                photo = images_data.get('image_intro') or images_data.get('image_fulltext') or images_data.get('image')
                        except:
                            pass
                    
                    conn.close()
                    return {
                        'joomla_id': joomla_id_val,
                        'name': name,
                        'photo': photo
                    }
                
                conn.close()
                return None
            
            import json
            joomla_id_val = row[0]
            name = row[1] if len(row) > 1 else None
            images_json = row[2] if len(row) > 2 else None
            photo = None
            
            if images_json:
                try:
                    images_data = json.loads(images_json) if isinstance(images_json, str) else images_json
                    if isinstance(images_data, dict):
                        photo = images_data.get('image_intro') or images_data.get('image_fulltext') or images_data.get('image')
                        if photo:
                            photo = str(photo).split('#')[0].strip()
                            if not photo or photo == 'null' or photo == '':
                                photo = None
                except:
                    pass
            
            if not photo and len(row) > 3:
                introtext = row[3] if len(row) > 3 else None
                fulltext = row[4] if len(row) > 4 else None
                import re
                for text in [introtext, fulltext]:
                    if text:
                        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', text)
                        if img_match:
                            photo = img_match.group(1)
                            break
            
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

def find_actor_photo_in_articles(actor_name):
    if not actor_name:
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
            normalized_name = actor_name.strip().lower()
            name_parts = normalized_name.split()
            
            if len(name_parts) < 2:
                conn.close()
                return None
            
            search_patterns = [normalized_name]
            if len(name_parts) >= 2:
                first_last = f"{name_parts[0]} {name_parts[-1]}"
                search_patterns.append(first_last)
                if name_parts[0] == 'aja':
                    search_patterns.append(f"aeja {name_parts[-1]}")
                elif name_parts[0] == 'aeja':
                    search_patterns.append(f"aja {name_parts[-1]}")
            
            tag_ids = []
            for pattern in search_patterns:
                tag_query = "SELECT id FROM wa8wx_tags WHERE LOWER(TRIM(title)) = %s AND published = 1"
                cursor.execute(tag_query, (pattern,))
                tag_row = cursor.fetchone()
                if tag_row:
                    tag_ids.append(tag_row[0])
            
            all_rows = []
            seen_ids = set()
            
            for pattern in search_patterns:
                query1 = """
                    SELECT c.id, c.title, c.images, c.introtext, c.fulltext 
                    FROM wa8wx_content c
                    WHERE LOWER(c.title) LIKE %s
                    AND c.state = 1 
                    ORDER BY c.id DESC 
                    LIMIT 3
                """
                title_pattern = f"%actor highlights%{pattern}%"
                cursor.execute(query1, (title_pattern,))
                rows = cursor.fetchall()
                
                for row in rows:
                    if row[0] not in seen_ids:
                        all_rows.insert(0, row)
                        seen_ids.add(row[0])
                
                query2 = """
                    SELECT c.id, c.title, c.images, c.introtext, c.fulltext 
                    FROM wa8wx_content c
                    WHERE (LOWER(c.introtext) LIKE %s OR LOWER(c.fulltext) LIKE %s) 
                    AND LOWER(c.title) NOT LIKE %s
                    AND LOWER(c.title) NOT LIKE %s
                    AND c.state = 1 
                    ORDER BY c.id DESC 
                    LIMIT 3
                """
                search_term = f"%{pattern}%"
                exclude_show = "%meet the cast%"
                exclude_cast = "%cast of%"
                cursor.execute(query2, (search_term, search_term, exclude_show, exclude_cast))
                rows = cursor.fetchall()
                
                for row in rows:
                    if row[0] not in seen_ids:
                        all_rows.append(row)
                        seen_ids.add(row[0])
                
                query3 = """
                    SELECT c.id, c.title, c.images, c.introtext, c.fulltext 
                    FROM wa8wx_content c
                    WHERE (LOWER(c.introtext) LIKE %s OR LOWER(c.fulltext) LIKE %s) 
                    AND (LOWER(c.title) LIKE %s OR LOWER(c.title) LIKE %s)
                    AND c.state = 1 
                    ORDER BY c.id DESC 
                    LIMIT 2
                """
                show_pattern1 = "%meet the cast%"
                show_pattern2 = "%cast of%"
                cursor.execute(query3, (search_term, search_term, show_pattern1, show_pattern2))
                rows = cursor.fetchall()
                
                for row in rows:
                    if row[0] not in seen_ids:
                        all_rows.append(row)
                        seen_ids.add(row[0])
            
            if tag_ids:
                try:
                    placeholders = ','.join(['%s'] * len(tag_ids))
                    query1 = f"""
                        SELECT DISTINCT c.id, c.title, c.images, c.introtext, c.fulltext 
                        FROM wa8wx_content c
                        INNER JOIN wa8wx_contentitem_tag_map m ON c.id = m.content_item_id
                        WHERE m.tag_id IN ({placeholders})
                        AND c.state = 1 
                        AND LOWER(c.title) NOT LIKE %s
                        AND LOWER(c.title) NOT LIKE %s
                        ORDER BY 
                            CASE WHEN LOWER(c.title) LIKE %s THEN 1 ELSE 2 END,
                            c.id DESC 
                        LIMIT 5
                    """
                    exclude_show = "%meet the cast%"
                    exclude_cast = "%cast of%"
                    actor_highlights = "%actor highlights%"
                    cursor.execute(query1, tuple(list(tag_ids) + [exclude_show, exclude_cast, actor_highlights]))
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        if row[0] not in seen_ids:
                            article_title = row[1] if len(row) > 1 else ""
                            if "actor highlights" in article_title.lower():
                                all_rows.insert(0, row)
                            else:
                                all_rows.append(row)
                            seen_ids.add(row[0])
                    
                    query2 = f"""
                        SELECT DISTINCT c.id, c.title, c.images, c.introtext, c.fulltext 
                        FROM wa8wx_content c
                        INNER JOIN wa8wx_contentitem_tag_map m ON c.id = m.content_item_id
                        WHERE m.tag_id IN ({placeholders})
                        AND c.state = 1 
                        AND (LOWER(c.title) LIKE %s OR LOWER(c.title) LIKE %s)
                        ORDER BY c.id DESC 
                        LIMIT 3
                    """
                    show_pattern1 = "%meet the cast%"
                    show_pattern2 = "%cast of%"
                    cursor.execute(query2, tuple(list(tag_ids) + [show_pattern1, show_pattern2]))
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        if row[0] not in seen_ids:
                            all_rows.append(row)
                            seen_ids.add(row[0])
                except Exception:
                    pass
            
            rows = all_rows
            
            individual_photo = None
            show_photo = None
            
            for row in rows:
                article_title = row[1] if len(row) > 1 else ""
                images_json = row[2] if len(row) > 2 else None
                introtext = row[3] if len(row) > 3 else None
                fulltext = row[4] if len(row) > 4 else None
                
                is_actor_highlights = "actor highlights" in article_title.lower()
                is_show_article = "meet the cast" in article_title.lower() or "cast of" in article_title.lower()
                
                photo = None
                
                if images_json:
                    try:
                        import json
                        images_data = json.loads(images_json) if isinstance(images_json, str) else images_json
                        if isinstance(images_data, dict):
                            photo = images_data.get('image_intro') or images_data.get('image_fulltext') or images_data.get('image')
                            if photo:
                                photo = str(photo).split('#')[0].strip()
                                if photo and photo != 'null' and photo != '':
                                    pass
                                else:
                                    photo = None
                    except:
                        pass
                
                if not photo:
                    import re
                    normalized_name = actor_name.strip().lower()
                    name_parts = normalized_name.split()
                    
                    for text in [introtext, fulltext]:
                        if text:
                            text_lower = text.lower()
                            actor_mentioned = False
                            
                            if len(name_parts) >= 2:
                                first_last = f"{name_parts[0]} {name_parts[-1]}"
                                if first_last in text_lower:
                                    actor_mentioned = True
                            
                            if not actor_mentioned and normalized_name in text_lower:
                                actor_mentioned = True
                            
                            if actor_mentioned or is_actor_highlights:
                                img_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', text)
                                if img_matches:
                                    for img_src in img_matches:
                                        if img_src and not img_src.startswith('data:'):
                                            photo = str(img_src).strip()
                                            break
                                    if photo:
                                        break
                
                if photo and photo.strip() and photo != 'null':
                    photo_url = None
                    if photo.startswith('http://') or photo.startswith('https://'):
                        photo_url = photo
                    elif photo.startswith('/'):
                        if not photo.startswith('//'):
                            photo_url = 'https://www.broadwayandmain.com' + photo
                        else:
                            photo_url = 'https:' + photo
                    elif photo.startswith('images/'):
                        photo_url = 'https://www.broadwayandmain.com/' + photo
                    else:
                        photo_url = 'https://www.broadwayandmain.com/images/' + photo.lstrip('/')
                    
                    if photo_url:
                        if is_actor_highlights:
                            individual_photo = photo_url
                            conn.close()
                            return individual_photo
                        elif not is_show_article:
                            if not individual_photo:
                                individual_photo = photo_url
                        else:
                            if not show_photo:
                                show_photo = photo_url
            
            if individual_photo:
                conn.close()
                return individual_photo
            
            if show_photo:
                conn.close()
                return show_photo
            
            conn.close()
            return None
            
        except Exception as e:
            conn.close()
            return None
            
    except Exception as e:
        return None

