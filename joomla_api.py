from flask import jsonify, request, Blueprint
from models import db, Person, Show, Theater, Production, Credit

joomla_api = Blueprint('joomla_api', __name__)

@joomla_api.route("/api/joomla/actor/<int:id>")
def joomla_api_actor(id):
    person = db.session.get(Person, id)
    if not person:
        return jsonify({"error": "Actor not found"}), 404
    
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
    
    return jsonify({
        'id': person.id,
        'name': person.name,
        'disciplines': person.disciplines,
        'credits': credits_data
    })

@joomla_api.route("/api/joomla/show/<int:id>")
def joomla_api_show(id):
    show = db.session.get(Show, id)
    if not show:
        return jsonify({"error": "Show not found"}), 404
    
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
        
        productions_data.append({
            'id': prod.id,
            'theater': {
                'id': prod.theater.id,
                'name': prod.theater.name,
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
        'name': theater.name,
        'joomla_id': theater.joomla_id,
        'shows': list(shows_data.values())
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

