from flask import jsonify, request, Blueprint
from models import db, Person, Show, Theater, Production, Credit

joomla_api = Blueprint('joomla_api', __name__)

def normalize_title_for_search(title):
    if not title:
        return ""
    return title.strip().lower()

def get_canonical_title(title):
    if not title:
        return title
    name = title.strip()
    if not name:
        return name
    return name.title()

@joomla_api.route("/api/joomla/actor/<int:id>")
def joomla_api_actor(id):
    person = db.session.get(Person, id)
    if not person:
        return jsonify({"error": "Actor not found"}), 404
    
    actor_photo = None
    
    if person.photo:
        from flask import url_for
        import os
        photo_path = os.path.join('static', person.photo)
        if os.path.exists(photo_path):
            actor_photo = url_for('static', filename=person.photo, _external=True)
            import time
            photo_mtime = os.path.getmtime(photo_path)
            actor_photo += f'?v={int(photo_mtime)}'
    
    if not actor_photo and person.joomla_id:
        from joomla_actor_fetch import get_actor_from_joomla
        joomla_actor_data = get_actor_from_joomla(person.joomla_id)
        if joomla_actor_data and joomla_actor_data.get('photo'):
            photo_path = joomla_actor_data.get('photo')
            if photo_path and str(photo_path).strip():
                photo_path = str(photo_path).strip()
                if photo_path.startswith('http://') or photo_path.startswith('https://'):
                    actor_photo = photo_path
                elif photo_path.startswith('/'):
                    if not photo_path.startswith('//'):
                        actor_photo = 'https://www.broadwayandmain.com' + photo_path
                    else:
                        actor_photo = 'https:' + photo_path
                elif photo_path.startswith('images/'):
                    actor_photo = 'https://www.broadwayandmain.com/' + photo_path
                else:
                    actor_photo = 'https://www.broadwayandmain.com/images/' + photo_path.lstrip('/')
    
    if not actor_photo:
        from joomla_actor_fetch import find_actor_photo_in_articles
        article_photo = find_actor_photo_in_articles(person.name)
        if article_photo:
            actor_photo = article_photo
    
    credits = db.session.query(Credit, Production, Show, Theater).join(
        Production, Credit.production_id == Production.id
    ).join(
        Show, Production.show_id == Show.id
    ).join(
        Theater, Production.theater_id == Theater.id
    ).filter(
        Credit.person_id == id
    ).order_by(Production.year.desc()).all()
    
    credits_data = []
    theaters_set = set()
    theaters_map_data = []
    roles_set = set()
    
    from joomla_theater_fetch import get_theater_from_joomla
    
    for credit, production, show, theater in credits:
        role_value = credit.role if credit.role else ''
        role_cleaned = role_value.strip() if role_value else ''
        
        credits_data.append({
            'role': role_value,
            'category': credit.category,
            'is_equity': credit.is_equity,
            'show': {
                'id': show.id,
                'title': show.title
            },
            'theater': {
                'id': theater.id,
                'name': theater.name,
                'joomla_id': theater.joomla_id
            },
            'year': production.year,
            'start_date': production.start_date,
            'end_date': production.end_date
        })
        
        if role_cleaned:
            roles_set.add(role_cleaned)
        
        if theater.id:
            theaters_set.add((theater.id, theater.name))
            
            if theater.joomla_id:
                joomla_theater_data = get_theater_from_joomla(theater.joomla_id)
                if joomla_theater_data:
                    theater_lat = joomla_theater_data.get('latitude')
                    theater_lng = joomla_theater_data.get('longitude')
                    theater_city = joomla_theater_data.get('city', '')
                    theater_state = joomla_theater_data.get('state', '')
                    
                    if theater_lat and theater_lng:
                        try:
                            theaters_map_data.append({
                                'id': theater.id,
                                'name': theater.name,
                                'lat': float(theater_lat),
                                'lng': float(theater_lng),
                                'city': theater_city or '',
                                'state': theater_state or ''
                            })
                        except (ValueError, TypeError):
                            pass
    
    theaters_list = [{'id': tid, 'name': tname} for tid, tname in theaters_set]
    
    roles_list = sorted(list(roles_set))
    roles_count = len(roles_list)
    
    disciplines_count = 0
    disciplines_list = []
    if person.disciplines:
        disciplines_list = [d.strip() for d in person.disciplines.split(',') if d.strip()]
        disciplines_count = len(disciplines_list)
    
    return jsonify({
        'id': person.id,
        'name': person.name,
        'disciplines': person.disciplines,
        'disciplines_count': disciplines_count,
        'roles': roles_list,
        'roles_count': roles_count,
        'photo': actor_photo,
        'credits': credits_data,
        'theaters': theaters_list,
        'theaters_map': theaters_map_data,
        'total_credits': len(credits_data)
    })

@joomla_api.route("/api/joomla/show/<int:id>")
def joomla_api_show(id):
    show = db.session.get(Show, id)
    if not show:
        return jsonify({"error": "Show not found"}), 404
    
    from joomla_theater_fetch import get_theater_from_joomla
    
    productions = Production.query.filter_by(show_id=id).order_by(Production.year.desc()).all()
    
    productions_data = []
    for prod in productions:
        credits = Credit.query.filter_by(production_id=prod.id).all()
        credits_data = []
        
        for credit in credits:
            credits_data.append({
                'person': {
                    'id': credit.person.id,
                    'name': credit.person.name
                },
                'role': credit.role,
                'category': credit.category,
                'is_equity': credit.is_equity
            })
        
        theater_name = prod.theater.name
        if prod.theater.joomla_id:
            try:
                joomla_data = get_theater_from_joomla(prod.theater.joomla_id)
                if joomla_data and joomla_data.get('name'):
                    theater_name = joomla_data.get('name')
            except:
                pass
        
        preview_image_url = None
        if prod.preview_image:
            from flask import url_for
            import os
            photo_path = os.path.join('static', prod.preview_image)
            if os.path.exists(photo_path):
                preview_image_url = url_for('static', filename=prod.preview_image, _external=True)
                import time
                photo_mtime = os.path.getmtime(photo_path)
                preview_image_url += f'?v={int(photo_mtime)}'
        
        productions_data.append({
            'id': prod.id,
            'theater': {
                'id': prod.theater.id,
                'name': theater_name,
                'joomla_id': prod.theater.joomla_id
            },
            'year': prod.year,
            'start_date': prod.start_date,
            'end_date': prod.end_date,
            'preview_image': prod.preview_image,
            'preview_image_url': preview_image_url,
            'youtube_url': prod.youtube_url,
            'credits': credits_data
        })
    
    return jsonify({
        'id': show.id,
        'title': show.title,
        'productions': productions_data
    })

@joomla_api.route("/api/joomla/theater/<int:id>")
def joomla_api_theater(id):
    theater = db.session.get(Theater, id)
    if not theater:
        return jsonify({"error": "Theater not found"}), 404
    
    if not theater.joomla_id:
        return jsonify({"error": "Theater not linked to Joomla"}), 404
    
    from joomla_theater_fetch import get_theater_from_joomla
    joomla_data = get_theater_from_joomla(theater.joomla_id)
    
    if not joomla_data:
        return jsonify({"error": "Theater data not found in Joomla"}), 404
    
    productions = Production.query.filter_by(theater_id=id).order_by(Production.year.desc()).all()
    
    shows_data = {}
    for prod in productions:
        show_id = prod.show_id
        if show_id not in shows_data:
            shows_data[show_id] = {
                'show': {
                    'id': prod.show.id,
                    'title': prod.show.title
                },
                'productions': []
            }
        
        credits = Credit.query.filter_by(production_id=prod.id).all()
        credits_data = []
        for credit in credits:
            credits_data.append({
                'person': {
                    'id': credit.person.id,
                    'name': credit.person.name
                },
                'role': credit.role,
                'category': credit.category,
                'is_equity': credit.is_equity
            })
        
        shows_data[show_id]['productions'].append({
            'id': prod.id,
            'year': prod.year,
            'start_date': prod.start_date,
            'end_date': prod.end_date,
            'preview_image': prod.preview_image,
            'youtube_url': prod.youtube_url,
            'credits': credits_data
        })
    
    return jsonify({
        'id': theater.id,
        'joomla_id': joomla_data.get('joomla_id'),
        'name': joomla_data.get('name'),
        'address': joomla_data.get('address'),
        'description': joomla_data.get('description'),
        'image': joomla_data.get('image'),
        'latitude': joomla_data.get('latitude'),
        'longitude': joomla_data.get('longitude'),
        'city': joomla_data.get('city'),
        'state': joomla_data.get('state'),
        'shows': list(shows_data.values())
    })

@joomla_api.route("/api/joomla/production/<int:id>")
def joomla_api_production(id):
    production = db.session.get(Production, id)
    if not production:
        return jsonify({"error": "Production not found"}), 404
    
    show = db.session.get(Show, production.show_id)
    theater = db.session.get(Theater, production.theater_id)
    
    credits = Credit.query.filter_by(production_id=id).all()
    credits_data = []
    
    for credit in credits:
        credits_data.append({
            'person': {
                'id': credit.person.id,
                'name': credit.person.name
            },
            'role': credit.role,
            'category': credit.category,
            'is_equity': credit.is_equity
        })
    
    return jsonify({
        'id': production.id,
        'show': {
            'id': show.id,
            'title': show.title
        },
        'theater': {
            'id': theater.id,
            'name': theater.name,
            'joomla_id': theater.joomla_id
        },
        'year': production.year,
        'start_date': production.start_date,
        'end_date': production.end_date,
        'preview_image': production.preview_image,
        'youtube_url': production.youtube_url,
        'credits': credits_data
    })

@joomla_api.route("/api/joomla/production-code/<show_code>")
def joomla_api_production_by_code(show_code):
    parts = show_code.split('_', 1)
    if len(parts) != 2:
        return jsonify({"error": "Invalid show code format. Expected: SHOWNAME_THEATERNAME"}), 400
    
    show_name_part = parts[0].strip().upper()
    theater_name_part = parts[1].strip().upper()
    
    all_shows = Show.query.all()
    matching_show = None
    for show in all_shows:
        show_normalized = show.title.upper().replace('THE ', '').replace(' ', '').replace('-', '').replace("'", "")
        show_name_normalized = show_name_part.replace(' ', '').replace('-', '').replace("'", "")
        if show_name_normalized in show_normalized or show_normalized.startswith(show_name_normalized):
            matching_show = show
            break
    
    if not matching_show:
        return jsonify({"error": f"Show not found for code: {show_name_part}"}), 404
    
    all_theaters = Theater.query.all()
    matching_theater = None
    for theater in all_theaters:
        theater_normalized = theater.name.upper().replace('THE ', '').replace(' ', '').replace('-', '').replace("'", "")
        theater_name_normalized = theater_name_part.replace(' ', '').replace('-', '').replace("'", "")
        if theater_name_normalized in theater_normalized or theater_normalized in theater_name_normalized:
            matching_theater = theater
            break
    
    if not matching_theater:
        return jsonify({"error": f"Theater not found for code: {theater_name_part}"}), 404
    
    production = Production.query.filter_by(
        show_id=matching_show.id,
        theater_id=matching_theater.id
    ).order_by(Production.year.desc()).first()
    
    if not production:
        return jsonify({"error": f"Production not found for {matching_show.title} at {matching_theater.name}"}), 404
    
    credits = Credit.query.filter_by(production_id=production.id).all()
    credits_data = []
    
    for credit in credits:
        credits_data.append({
            'person': {
                'id': credit.person.id,
                'name': credit.person.name
            },
            'role': credit.role,
            'category': credit.category,
            'is_equity': credit.is_equity
        })
    
    return jsonify({
        'id': production.id,
        'show': {
            'id': matching_show.id,
            'title': matching_show.title
        },
        'theater': {
            'id': matching_theater.id,
            'name': matching_theater.name,
            'joomla_id': matching_theater.joomla_id
        },
        'year': production.year,
        'start_date': production.start_date,
        'end_date': production.end_date,
        'preview_image': production.preview_image,
        'youtube_url': production.youtube_url,
        'credits': credits_data
    })

@joomla_api.route("/api/joomla/available-codes")
def joomla_api_available_codes():
    shows = Show.query.all()
    theaters = Theater.query.all()
    productions = Production.query.all()
    
    available_codes = []
    
    for production in productions:
        show = db.session.get(Show, production.show_id)
        theater = db.session.get(Theater, production.theater_id)
        
        if show and theater:
            show_code_part = show.title.upper().replace('THE ', '').replace(' ', '_').replace('-', '_').replace("'", "").replace(',', '')[:20]
            theater_code_part = theater.name.upper().replace('THE ', '').replace(' ', '_').replace('-', '_').replace("'", "").replace(',', '')[:20]
            code = f"{show_code_part}_{theater_code_part}"
            
            available_codes.append({
                'code': code,
                'show': show.title,
                'theater': theater.name,
                'year': production.year,
                'production_id': production.id
            })
    
    return jsonify({
        'available_codes': available_codes,
        'instructions': 'Use the "code" value as your Show Code in the Joomla module. Format: SHOWNAME_THEATERNAME'
    })

@joomla_api.route("/api/joomla/search")
def joomla_api_search():
    query = request.args.get('q', '').strip()
    filter_type = request.args.get('type', 'all')
    equity_filter = request.args.get('equity', 'all')
    
    results = {
        'actors': [],
        'shows': [],
        'theaters': []
    }
    
    seen_actor_ids = set()
    
    if query:
        if filter_type in ['all', 'actors']:
            if filter_type == 'actors':
                person_ids_query = db.session.query(Person.id)\
                    .join(Credit, Person.id == Credit.person_id)\
                    .join(Production, Credit.production_id == Production.id)\
                    .join(Show, Production.show_id == Show.id)\
                    .join(Theater, Production.theater_id == Theater.id)\
                    .filter(Person.name.ilike(f'%{query}%'))
            else:
                person_ids_query = db.session.query(Person.id)\
                    .join(Credit, Person.id == Credit.person_id)\
                    .join(Production, Credit.production_id == Production.id)\
                    .join(Show, Production.show_id == Show.id)\
                    .join(Theater, Production.theater_id == Theater.id)\
                    .filter(
                        (Person.name.ilike(f'%{query}%')) |
                        (Show.title.ilike(f'%{query}%')) |
                        (Theater.name.ilike(f'%{query}%'))
                    )
            
            person_ids = [person_id for person_id, in person_ids_query.distinct().all()]
            persons = Person.query.filter(Person.id.in_(person_ids)).all()
            
            person_credits_map = {}
            seen_normalized = set()
            
            for person in persons:
                if not person or not person.name:
                    continue
                    
                from app import normalize_name
                normalized_name = normalize_name(person.name)
                
                if not normalized_name:
                    continue
                
                normalized_key = normalized_name.strip().lower()
                
                if normalized_key not in person_credits_map:
                    person_credits_map[normalized_key] = {
                        'display_name': normalized_name,
                        'ids': set(),
                        'persons': []
                    }
                    seen_normalized.add(normalized_key)
                
                if person.id not in person_credits_map[normalized_key]['ids']:
                    person_credits_map[normalized_key]['ids'].add(person.id)
                    person_credits_map[normalized_key]['persons'].append(person)
            
            for normalized_key, data in person_credits_map.items():
                all_person_ids = list(data['ids'])
                if not all_person_ids:
                    continue
                    
                credits_query = Credit.query.filter(Credit.person_id.in_(all_person_ids))
                
                if equity_filter == 'equity':
                    credits_query = credits_query.filter_by(is_equity=True)
                elif equity_filter == 'non-equity':
                    credits_query = credits_query.filter_by(is_equity=False)
                
                filtered_credits_count = credits_query.count()
                
                if filtered_credits_count > 0:
                    valid_person_ids = []
                    person_credit_counts = {}
                    
                    for pid in all_person_ids:
                        try:
                            person_check = db.session.get(Person, pid)
                            if person_check and person_check.id == pid and person_check.name:
                                person_credits = Credit.query.filter_by(person_id=pid).count()
                                if person_credits > 0:
                                    valid_person_ids.append(pid)
                                    person_credit_counts[pid] = person_credits
                        except:
                            continue
                    
                    if not valid_person_ids:
                        continue
                    
                    primary_person_id = max(valid_person_ids, key=lambda pid: person_credit_counts.get(pid, 0))
                    
                    if primary_person_id not in seen_actor_ids:
                        final_person_check = db.session.get(Person, primary_person_id)
                        if final_person_check and final_person_check.id == primary_person_id and final_person_check.name:
                            test_credits = Credit.query.filter_by(person_id=primary_person_id).count()
                            if test_credits > 0:
                                seen_actor_ids.add(primary_person_id)
                                results['actors'].append({
                                    'id': primary_person_id,
                                    'name': data['display_name'],
                                    'credits_count': filtered_credits_count
                                })
        
        if filter_type in ['all', 'shows']:
            productions = db.session.query(Production, Show, Theater)\
                .join(Show, Production.show_id == Show.id)\
                .join(Theater, Production.theater_id == Theater.id)\
                .filter(Show.title.ilike(f'%{query}%'))\
                .all()
            
            for production, show, theater in productions:
                if not theater.joomla_id:
                    continue
                
                try:
                    from app import get_theater_name_from_joomla
                    theater_name = get_theater_name_from_joomla(theater.joomla_id)
                except:
                    continue
                
                results['shows'].append({
                    'production_id': production.id,
                    'show_id': show.id,
                    'show_title': get_canonical_title(show.title),
                    'theater_name': theater_name,
                    'year': production.year,
                    'start_date': production.start_date,
                    'end_date': production.end_date
                })
        
        if filter_type in ['all', 'theaters']:
            theaters = Theater.query.filter(
                Theater.name.ilike(f'%{query}%')
            ).all()
            
            for theater in theaters:
                prod_count = Production.query.filter_by(theater_id=theater.id).count()
                results['theaters'].append({
                    'id': theater.id,
                    'name': theater.name,
                    'joomla_id': theater.joomla_id,
                    'productions_count': prod_count
                })
    
    return jsonify(results)

