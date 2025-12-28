import os
import json
from flask import Flask, render_template, request, jsonify
from models import db, Theater, Show, Production, Person, Credit
from extraction_service import process_pdf
from werkzeug.utils import secure_filename
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALL_CATEGORIES = [
    'Cast',
    'Creative',
    'Musician',
    'Crew',
    'Swings',
    'Understudies',
    'Dance Captain',
    'Ensemble'
]

db.init_app(app)

def init_db():
    with app.app_context():
        db.create_all()
        if not Theater.query.first():
            db.session.add(Theater(name="THE ARGYLE THEATRE",  latitude="40.7128", longitude="-74.0060", city="New York", state="NY"))
            db.session.add(Theater(name="The Gateway",  latitude="40.7589", longitude="-73.9851", city="New York", state="NY"))
            db.session.add(Theater(name="John W. Engeman Theater", latitude="40.9012", longitude="-73.3434", city="Northport", state="NY"))
            db.session.commit()
        else:
            for theater in Theater.query.all():
                if not theater.latitude or not theater.longitude:
                    if theater.name == "THE ARGYLE THEATRE":
                        theater.latitude = "40.7128"
                        theater.longitude = "-74.0060"
                        theater.city = "New York"
                        theater.state = "NY"
                    elif theater.name == "The Gateway":
                        theater.latitude = "40.7589"
                        theater.longitude = "-73.9851"
                        theater.city = "New York"
                        theater.state = "NY"
                    elif theater.name == "John W. Engeman Theater":
                        theater.latitude = "40.9012"
                        theater.longitude = "-73.3434"
                        theater.city = "Northport"
                        theater.state = "NY"
            db.session.commit()

init_db()

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload():
    path = None
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        if file and file.filename.endswith(".pdf"):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            
            try:
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
                
                max_size = 10 * 1024 * 1024
                if file_size > max_size:
                    return jsonify({"error": f"File too large. Maximum size is {max_size // (1024*1024)}MB"}), 400
            except:
                pass
            
            file.save(path)
            
            try:
                data = process_pdf(path)
            except Exception as e:
                import traceback
                error_msg = str(e)
                traceback.print_exc()
                return jsonify({"error": f"Extraction failed: {error_msg}"}), 500
            finally:
                import time
                time.sleep(0.1)
                max_retries = 5
                for attempt in range(max_retries):
                    try:
                        if path and os.path.exists(path):
                            os.remove(path)
                        break
                    except PermissionError:
                        if attempt < max_retries - 1:
                            time.sleep(0.2)
                        else:
                            print(f"Warning: Could not delete {path} - file may be locked")
                    
            if not data:
                from config import Config
                if Config.TEST_MODE:
                    return jsonify({"error": "Extraction failed: Test mode mock data generation failed"}), 500
                else:
                    return jsonify({
                        "error": "Extraction failed: No data returned from API",
                        "message": "This may be due to API region restrictions. Enable TEST_MODE=true in .env to test with mock data."
                    }), 500

            all_credits = []
            categories_map = [
                ('cast', 'Cast'), 
                ('creative', 'Creative'), 
                ('musicians', 'Musician'), 
                ('crew', 'Crew'),
                ('swings', 'Swings'),
                ('understudies', 'Understudies'),
                ('dance_captains', 'Dance Captain')
            ]
            
            def split_dual_role(role_text):
                role_mappings = {
                    'directed': 'Director',
                    'choreographed': 'Choreographer',
                    'written': 'Writer',
                    'produced': 'Producer',
                    'designed': 'Designer',
                    'lighting': 'Lighting Designer',
                    'sound': 'Sound Designer',
                    'costume': 'Costume Designer',
                    'set': 'Set Designer',
                    'scenic': 'Scenic Designer'
                }
                
                if '&' in role_text.lower() or 'and' in role_text.lower():
                    parts = []
                    role_lower = role_text.lower()
                    
                    if 'directed' in role_lower and 'choreographed' in role_lower:
                        parts.append('Director')
                        parts.append('Choreographer')
                    elif 'directed' in role_lower and 'written' in role_lower:
                        parts.append('Director')
                        parts.append('Writer')
                    elif 'written' in role_lower and 'directed' in role_lower:
                        parts.append('Writer')
                        parts.append('Director')
                    else:
                        for key, mapped_role in role_mappings.items():
                            if key in role_lower:
                                parts.append(mapped_role)
                    
                    if not parts:
                        parts = [role_text]
                    
                    return parts
                return [role_text]
            
            for cat_key, cat_name in categories_map:
                items = data.get(cat_key, [])
                if items:
                    for item in items:
                        if isinstance(item, str):
                            is_eq = False
                            clean_name = item
                            if "*" in item:
                                is_eq = True
                                clean_name = item.replace("*", "").strip()
                            
                            all_credits.append({
                                'cat': cat_name,
                                'role': cat_name,
                                'actor': clean_name,
                                'is_equity': is_eq
                            })
                        elif isinstance(item, dict):
                            role = item.get('role', cat_name)
                            actor = item.get('actor', '')
                            is_equity = item.get('is_equity', False)
                            
                            split_roles = split_dual_role(role)
                            
                            for split_role in split_roles:
                                all_credits.append({
                                    'cat': cat_name,
                                    'role': split_role,
                                    'actor': actor,
                                    'is_equity': is_equity
                                })
                        
            ensemble_list = data.get('ensemble', [])
            for name in ensemble_list:
                 is_eq = False
                 clean_name = name
                 if "*" in name:
                     is_eq = True
                     clean_name = name.replace("*", "").strip()
                 
                 all_credits.append({
                     'cat': 'Ensemble',
                     'role': 'Ensemble',
                     'actor': clean_name,
                     'is_equity': is_eq
                 })

            data['all_credits'] = all_credits

            return render_template("review.html", data=data, filename=filename)
        
        return jsonify({"error": "Invalid file type"}), 400
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
        return jsonify({"error": f"Internal server error: {error_msg}"}), 500

@app.route("/dashboard")
def dashboard():
    productions = Production.query.all()
    return render_template("dashboard.html", productions=productions)

@app.route("/edit/<int:id>")
def edit(id):
    production = db.session.get(Production, id)
    if not production:
        return "Production not found", 404
        
    all_credits = []
    for credit in production.credits:
        all_credits.append({
            "cat": credit.category,
            "role": credit.role,
            "actor": credit.person.name,
            "is_equity": credit.is_equity
        })
        
    data = {
        "show_title": production.show.title,
        "theatre_name": production.theater.name,
        "production_year": production.year,
        "start_date": production.start_date,
        "end_date": production.end_date,
        "preview_image": production.preview_image,
        "youtube_url": production.youtube_url,
        "all_credits": all_credits,
        "production_id": production.id
    }
    
    return render_template("review.html", data=data, filename=f"Edit: {production.show.title}")

@app.route("/save", methods=["POST"])
def save():
    data = request.json
    try:
        production_id = data.get("production_id")
        override = data.get("override", False)
        
        show_title = data.get("show_title", "Unknown Show")
        show = Show.query.filter_by(title=show_title).first()
        if not show:
            show = Show(title=show_title)
            db.session.add(show)
            db.session.flush()

        theater_name = data.get("theatre_name")
        theater = Theater.query.filter(Theater.name.ilike(theater_name)).first()
        if not theater:
             theater = Theater(name=theater_name)
             db.session.add(theater)
             db.session.flush()

        if production_id:
            production = db.session.get(Production, production_id)
            if not production:
                return jsonify({"error": "Production not found"}), 404
            
            production.show_id = show.id
            production.theater_id = theater.id
            year_val = data.get("production_year")
            production.year = int(year_val) if year_val else 2025
            production.start_date = data.get("start_date")
            production.end_date = data.get("end_date")
            production.preview_image = data.get("preview_image")
            production.youtube_url = data.get("youtube_url")
            
            Credit.query.filter_by(production_id=production.id).delete()
            
        else:
            try:
                raw_year = data.get("production_year")
                final_year = int(raw_year) if raw_year else 2025
            except (ValueError, TypeError):
                final_year = 2025
            
            existing = Production.query.filter_by(
                theater_id=theater.id,
                show_id=show.id,
                year=final_year
            ).first()
            
            if existing and not override:
                return jsonify({
                    "error": "Duplicate production detected",
                    "message": f"A production of '{show_title}' at '{theater_name}' in {final_year} already exists.",
                    "existing_id": existing.id
                }), 409
            elif existing and override:
                production_id = existing.id
                production = db.session.get(Production, production_id)
            
                production.show_id = show.id
                production.theater_id = theater.id
                year_val = data.get("production_year")
                production.year = int(year_val) if year_val else 2025
                production.start_date = data.get("start_date")
                production.end_date = data.get("end_date")
                production.preview_image = data.get("preview_image")
                production.youtube_url = data.get("youtube_url")
            
                Credit.query.filter_by(production_id=production.id).delete()

            if not production_id:
                production = Production(
                    theater_id=theater.id,
                    show_id=show.id,
                    year=final_year,
                    start_date=data.get("start_date"),
                    end_date=data.get("end_date"),
                    preview_image=data.get("preview_image"),
                    youtube_url=data.get("youtube_url")
                )
                db.session.add(production)
                db.session.flush()

        for item in data.get("credits", []):
            actor_name = item.get("actor")
            role_name = item.get("role")
            category = item.get("category", "Cast")
            is_equity = item.get("is_equity", False)
            
            if not actor_name: continue

            person = Person.query.filter_by(name=actor_name).first()
            if not person:
                person = Person(name=actor_name, disciplines=category)
                db.session.add(person)
                db.session.flush()
            
            credit = Credit(
                production_id=production.id,
                person_id=person.id,
                role=role_name,
                category=category,
                is_equity=is_equity
            )
            db.session.add(credit)

        db.session.commit()
        return jsonify({"success": True, "message": "Saved successfully!"})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/delete/<int:id>", methods=["POST"])
def delete_production(id):
    try:
        production = db.session.get(Production, id)
        if not production:
            return jsonify({"error": "Production not found"}), 404
            
        db.session.delete(production)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/download/<int:id>")
def download_production(id):
    try:
        production = db.session.get(Production, id)
        if not production:
            return "Production not found", 404

        all_credits = []
        for credit in production.credits:
            all_credits.append({
                "category": credit.category,
                "role": credit.role,
                "actor": credit.person.name,
                "is_equity": credit.is_equity
            })
            
        data = {
            "show_title": production.show.title,
            "theatre_name": production.theater.name,
            "production_year": production.year,
            "start_date": production.start_date,
            "end_date": production.end_date,
            "preview_image": production.preview_image,
            "youtube_url": production.youtube_url,
            "credits": all_credits
        }
        
        safe_title = secure_filename(production.show.title)
        filename = f"{safe_title}_{production.year}.json"
        
        return jsonify(data), 200, {'Content-Disposition': f'attachment; filename={filename}'}

    except Exception as e:
        return str(e), 500

@app.route("/public/actor/<int:id>")
def public_actor(id):
    person = db.session.get(Person, id)
    if not person:
        return "Actor not found", 404
    
    credits_query = db.session.query(Credit, Production, Show, Theater).join(
        Production, Credit.production_id == Production.id
    ).join(
        Show, Production.show_id == Show.id
    ).join(
        Theater, Production.theater_id == Theater.id
    ).filter(
        Credit.person_id == id
    ).order_by(Production.year.desc(), Show.title)
    
    all_credits = credits_query.all()
    
    credits_by_discipline = {}
    theaters_set = set()
    
    for credit, production, show, theater in all_credits:
        discipline = credit.category
        if discipline not in credits_by_discipline:
            credits_by_discipline[discipline] = []
        
        credits_by_discipline[discipline].append({
            'role': credit.role,
            'show_title': show.title,
            'show_id': show.id,
            'theater_name': theater.name,
            'theater_id': theater.id,
            'year': production.year,
            'is_equity': credit.is_equity,
            'production_id': production.id
        })
        
        theaters_set.add((theater.id, theater.name, theater.latitude, theater.longitude, theater.city, theater.state))
    
    theaters_list = []
    theaters_with_coords = []
    for tid, tname, lat, lng, city, state in theaters_set:
        theaters_list.append({'id': tid, 'name': tname})
        if lat and lng:
            try:
                theaters_with_coords.append({
                    'id': tid,
                    'name': tname,
                    'lat': float(lat),
                    'lng': float(lng),
                    'city': city or '',
                    'state': state or ''
                })
            except (ValueError, TypeError):
                pass
    
    total_credits = sum(len(credits) for credits in credits_by_discipline.values())
    
    return render_template("public_actor.html", 
                         person=person, 
                         credits_by_discipline=credits_by_discipline,
                         theaters=theaters_list,
                         theaters_map=theaters_with_coords,
                         total_credits=total_credits)

@app.route("/public/show/<int:id>")
def public_show(id):
    show = db.session.get(Show, id)
    if not show:
        return "Show not found", 404
    
    productions = Production.query.filter_by(show_id=id).order_by(Production.year.desc()).all()
    
    all_credits_by_production = {}
    for prod in productions:
        credits = Credit.query.filter_by(production_id=prod.id).all()
        credits_by_category = {}
        
        for credit in credits:
            cat = credit.category
            if cat not in credits_by_category:
                credits_by_category[cat] = []
            credits_by_category[cat].append({
                'person_name': credit.person.name,
                'person_id': credit.person.id,
                'role': credit.role,
                'is_equity': credit.is_equity
            })
        
        all_credits_by_production[prod.id] = {
            'production': prod,
            'theater': prod.theater,
            'credits': credits_by_category
        }
    
    return render_template("public_show.html", 
                         show=show, 
                         productions_data=all_credits_by_production)

@app.route("/public/theater/<int:id>")
def public_theater(id):
    theater = db.session.get(Theater, id)
    if not theater:
        return "Theater not found", 404
    
    productions = Production.query.filter_by(theater_id=id).order_by(Production.year.desc(), Production.start_date).all()
    
    shows_data = {}
    for prod in productions:
        show_id = prod.show_id
        if show_id not in shows_data:
            shows_data[show_id] = {
                'show': prod.show,
                'productions': []
            }
        shows_data[show_id]['productions'].append(prod)
    
    return render_template("public_theater.html", 
                         theater=theater, 
                         shows_data=shows_data)

@app.route("/admin/add-sample-data")
def add_sample_data_route():
    try:
        from add_sample_data import add_sample_data
        add_sample_data()
        return jsonify({"success": True, "message": "Sample data added successfully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/public/search")
def public_search():
    query = request.args.get('q', '').strip()
    filter_type = request.args.get('type', 'all')
    equity_filter = request.args.get('equity', 'all')
    
    results = {
        'actors': [],
        'shows': [],
        'theaters': []
    }
    
    all_categories = ALL_CATEGORIES

    if query:
        is_category_filter = filter_type not in ['all', 'actors', 'shows', 'theaters']
        
        if filter_type in ['all', 'actors'] or is_category_filter:
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

            if is_category_filter:
                person_ids_query = person_ids_query.filter(Credit.category.ilike(filter_type))

            person_ids = [person_id for person_id, in person_ids_query.distinct().all()]
            persons = Person.query.filter(Person.id.in_(person_ids)).all()
            
            for person in persons:
                credits_query = Credit.query.filter_by(person_id=person.id)
                if is_category_filter:
                    credits_query = credits_query.filter(Credit.category.ilike(filter_type))

                if equity_filter == 'equity':
                    credits_query = credits_query.filter_by(is_equity=True)
                elif equity_filter == 'non-equity':
                    credits_query = credits_query.filter_by(is_equity=False)
                
                filtered_credits_count = credits_query.count()

                if filtered_credits_count > 0:
                    results['actors'].append({
                        'id': person.id,
                        'name': person.name,
                        'credits_count': filtered_credits_count
                    })
        
        if filter_type in ['all', 'shows']:
            shows = Show.query.filter(
                Show.title.ilike(f'%{query}%')
            ).all()
            
            for show in shows:
                prod_count = Production.query.filter_by(show_id=show.id).count()
                if prod_count > 0:
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
                if prod_count > 0:
                    results['theaters'].append({
                        'id': theater.id,
                        'name': theater.name,
                        'productions_count': prod_count
                    })
    
    return render_template("public_search.html", 
                         query=query,
                         filter_type=filter_type,
                         equity_filter=equity_filter,
                         results=results,
                         categories=all_categories)

@app.route("/autocomplete/theaters")
def autocomplete_theaters():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    theaters = Theater.query.filter(Theater.name.ilike(f'%{query}%')).limit(10).all()
    return jsonify([theater.name for theater in theaters])

@app.route("/autocomplete/search")
def autocomplete_search():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])
    
    suggestions = []
    
    actors = Person.query.filter(Person.name.ilike(f'%{query}%')).limit(5).all()
    for actor in actors:
        suggestions.append(actor.name)
    
    shows = Show.query.filter(Show.title.ilike(f'%{query}%')).limit(5).all()
    for show in shows:
        suggestions.append(show.title)
    
    theaters = Theater.query.filter(Theater.name.ilike(f'%{query}%')).limit(5).all()
    for theater in theaters:
        suggestions.append(theater.name)
    
    return jsonify(suggestions[:10])

@app.route("/edit_understudies/<int:production_id>", methods=["POST"])
def edit_understudies(production_id):
    data = request.json
    understudies = data.get("understudies", [])

    try:
        production = db.session.get(Production, production_id)
        if not production:
            return jsonify({"error": "Production not found"}), 404

        Credit.query.filter_by(production_id=production.id, category="Understudies").delete()

        for name in understudies:
            person = Person.query.filter_by(name=name).first()
            if not person:
                person = Person(name=name, disciplines="Understudies")
                db.session.add(person)
                db.session.flush()
            
            credit = Credit(
                production_id=production.id,
                person_id=person.id,
                role="Understudy",
                category="Understudies",
                is_equity=False 
            )
            db.session.add(credit)
        
        db.session.commit()
        return jsonify({"success": True, "message": "Understudies updated successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


from joomla_api import joomla_api
app.register_blueprint(joomla_api)

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)