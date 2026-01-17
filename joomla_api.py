from flask import jsonify, request, Blueprint
from models import db, Person, Show, Theater, Production, Credit

joomla_api = Blueprint('joomla_api', __name__)

@joomla_api.route("/api/joomla/actor/<int:id>")
def joomla_api_actor(id):
    person = db.session.get(Person, id)
    if not person:
        return jsonify({"error": "Actor not found"}), 404
    
    actor_photo = None
    if person.joomla_id:
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
    
    if not actor_photo and person.photo:
        from flask import url_for
        actor_photo = url_for('static', filename=person.photo, _external=True)
    
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
    for credit, production, show, theater in credits:
        credits_data.append({
            'role': credit.role,
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
        if theater.id:
            theaters_set.add((theater.id, theater.name))
    
    theaters_list = [{'id': tid, 'name': tname} for tid, tname in theaters_set]
    
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
        'photo': actor_photo,
        'credits': credits_data,
        'theaters': theaters_list,
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
    
    if query:
        if filter_type in ['all', 'actors']:
            persons = Person.query.filter(
                Person.name.ilike(f'%{query}%')
            ).all()
            
            for person in persons:
                credits_count = Credit.query.filter_by(person_id=person.id).count()
                if equity_filter == 'equity':
                    credits_count = Credit.query.filter_by(person_id=person.id, is_equity=True).count()
                    if credits_count == 0:
                        continue
                elif equity_filter == 'non-equity':
                    credits_count = Credit.query.filter_by(person_id=person.id, is_equity=False).count()
                    if credits_count == 0:
                        continue
                
                results['actors'].append({
                    'id': person.id,
                    'name': person.name,
                    'credits_count': credits_count
                })
        
        if filter_type in ['all', 'shows']:
            shows = Show.query.filter(
                Show.title.ilike(f'%{query}%')
            ).all()
            
            for show in shows:
                prod_count = Production.query.filter_by(show_id=show.id).count()
                results['shows'].append({
                    'id': show.id,
                    'title': show.title,
                    'productions_count': prod_count
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

