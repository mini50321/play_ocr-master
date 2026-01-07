import os
import json
import logging
import sys
import traceback
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, session, url_for as flask_url_for, make_response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from models import db, Theater, Show, Production, Person, Credit, AdminSettings
from extraction_service import process_pdf, GeminiQuotaExceededError, GeminiAPIError, GeminiAPIDisabledError
from config import Config
from PIL import Image

APPLICATION_ROOT = os.getenv('APPLICATION_ROOT', '/')
if APPLICATION_ROOT != '/':
    if not APPLICATION_ROOT.startswith('/'):
        APPLICATION_ROOT = '/' + APPLICATION_ROOT
    if not APPLICATION_ROOT.endswith('/'):
        APPLICATION_ROOT = APPLICATION_ROOT + '/'

app = Flask(__name__, static_url_path=APPLICATION_ROOT.rstrip('/') + '/static')
app.config.from_object(Config)
app.config['APPLICATION_ROOT'] = APPLICATION_ROOT
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(os.path.join("static", "profiles"), exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the admin area.'

class AdminUser(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return AdminUser(user_id)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ]
)

try:
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)
except Exception as e:
    print(f"Could not create log file (this is OK on Render.com): {e}")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def normalize_name(name):
    if not name:
        return name
    name = name.strip()
    if not name:
        return name
    
    return name.title()

def get_theater_name_from_joomla(joomla_id):
    """Get theater name from Joomla database by joomla_id. Raises error if not found."""
    if not joomla_id:
        raise ValueError("Theater joomla_id is required")
    from joomla_theater_fetch import get_theater_from_joomla
    joomla_data = get_theater_from_joomla(joomla_id)
    if not joomla_data:
        raise ValueError(f"Theater data not found in Joomla for joomla_id: {joomla_id}")
    return joomla_data.get('name')

def find_or_match_theater(theater_name):
    if not theater_name:
        return None
    
    theater_name = theater_name.strip()
    if not theater_name:
        return None
    
    exact_match = Theater.query.filter(Theater.name.ilike(theater_name)).first()
    if exact_match and exact_match.joomla_id:
        return exact_match
    
    normalized_name = theater_name.upper().strip()
    normalized_name = normalized_name.replace("THEATRE", "THEATER")
    normalized_name = normalized_name.replace("THE ", "").strip()
    
    all_theaters = Theater.query.filter(Theater.joomla_id.isnot(None)).all()
    
    best_match = None
    best_score = 0
    
    for t in all_theaters:
        t_normalized = t.name.upper().replace("THEATRE", "THEATER").replace("THE ", "").strip()
        
        if normalized_name == t_normalized:
            return t
        
        if len(normalized_name) > 5 and len(t_normalized) > 5:
            if normalized_name in t_normalized or t_normalized in normalized_name:
                overlap = min(len(normalized_name), len(t_normalized))
                if overlap > best_score:
                    best_score = overlap
                    best_match = t
    
    if best_match and best_score > 10:
        return best_match
    
    return exact_match if exact_match else None

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
        
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            
            if 'theater' in inspector.get_table_names():
                theater_columns = [col['name'] for col in inspector.get_columns('theater')]
                
                with db.engine.connect() as conn:
                    if 'address' not in theater_columns:
                        conn.execute(text('ALTER TABLE theater ADD COLUMN address TEXT'))
                        conn.commit()
                    if 'description' not in theater_columns:
                        conn.execute(text('ALTER TABLE theater ADD COLUMN description TEXT'))
                        conn.commit()
                    if 'image' not in theater_columns:
                        conn.execute(text('ALTER TABLE theater ADD COLUMN image VARCHAR(500)'))
                        conn.commit()
        except Exception as e:
            print(f"Migration check: {e}")
        
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
        
        AdminSettings.get_or_create()

init_db()

@app.before_request
def log_request_info():
    if request.path == '/favicon.ico' or request.path.endswith('/favicon.ico'):
        from flask import Response
        return Response("", status=204)
    
    if request.path == '/upload':
        logger.info(f"Request: {request.method} {request.path}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Content-Length: {request.content_length}")

@app.after_request
def log_response_info(response):
    if request.path == '/upload' and response.status_code >= 400:
        logger.error(f"Response status: {response.status_code}")
        try:
            if response.is_json:
                logger.error(f"Response JSON: {response.get_json()}")
        except:
            pass
    return response

@app.errorhandler(500)
def internal_error(error):
    if request.path == '/favicon.ico' or request.path.endswith('/favicon.ico'):
        from flask import Response
        return Response("", status=204)
    
    logger.error("=" * 80)
    logger.error("FLASK 500 ERROR HANDLER TRIGGERED")
    logger.error(f"Error: {error}")
    logger.error(traceback.format_exc())
    logger.error("=" * 80)
    
    if request.is_json or request.path == '/upload':
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please check the logs for details."
        }), 500
    else:
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please check the logs for details."
        }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    if request.path == '/favicon.ico' or request.path.endswith('/favicon.ico'):
        from flask import Response
        return Response("", status=204)
    
    logger.error("=" * 80)
    logger.error("UNHANDLED EXCEPTION CAUGHT BY FLASK ERROR HANDLER")
    logger.error(f"Exception type: {type(e).__name__}")
    logger.error(f"Exception message: {str(e)}")
    logger.error(traceback.format_exc())
    logger.error("=" * 80)
    
    if isinstance(e, MemoryError):
        error_response = {
            "error": "Out of memory",
            "message": "The server ran out of memory processing your request. Please try a smaller file."
        }
    elif isinstance(e, TimeoutError):
        error_response = {
            "error": "Request timeout",
            "message": "The request took too long to process. Please try again."
        }
    else:
        error_response = {
            "error": f"Server error: {type(e).__name__}",
            "message": f"An error occurred: {str(e)}"
        }
    
    if request.is_json or request.path == '/upload':
        return jsonify(error_response), 500
    else:
        return jsonify(error_response), 500

@app.context_processor
def inject_url_for():
    def url_for(endpoint, **values):
        url = flask_url_for(endpoint, **values)
        if APPLICATION_ROOT != '/':
            root = APPLICATION_ROOT.rstrip('/')
            if not url.startswith(root):
                url = root + url
        return url
    return dict(url_for=url_for, current_user=current_user)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        authenticated = False
        
        try:
            settings = AdminSettings.query.first()
            if settings and username == settings.username:
                if check_password_hash(settings.password_hash, password):
                    authenticated = True
        except:
            pass
        
        if not authenticated:
            if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
                authenticated = True
        
        if authenticated:
            user = AdminUser(username)
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or flask_url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password")
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    next_page = request.args.get("next")
    logout_user()
    if next_page:
        return redirect(flask_url_for("login") + f"?next={next_page}")
    return redirect(flask_url_for("public_search"))

@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.route("/")
@login_required
def index():
    return render_template("upload.html")

def ensure_json_response(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error("=" * 80)
            logger.error("EXCEPTION IN UPLOAD ROUTE WRAPPER")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception message: {str(e)}")
            logger.error(traceback.format_exc())
            logger.error("=" * 80)
            
            if isinstance(e, MemoryError):
                return jsonify({
                    "error": "Out of memory",
                    "message": "The server ran out of memory. Please try a smaller file."
                }), 500
            elif isinstance(e, TimeoutError) or 'timeout' in str(e).lower():
                return jsonify({
                    "error": "Request timeout",
                    "message": "The request took too long. Please try again."
                }), 500
            else:
                return jsonify({
                    "error": f"Upload failed: {type(e).__name__}",
                    "message": f"An error occurred: {str(e)}"
                }), 500
    wrapper.__name__ = func.__name__
    return wrapper

@app.route("/upload", methods=["POST"])
@login_required
@ensure_json_response
def upload():
    path = None
    upload_start_time = datetime.now()
    filename = None
    
    try:
        logger.info("=" * 80)
        logger.info(f"UPLOAD REQUEST STARTED at {upload_start_time}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Content type: {request.content_type}")
        logger.info(f"Content length: {request.content_length}")
        
        if "file" not in request.files:
            logger.warning("Upload failed: No file part in request")
            return jsonify({"error": "No file part"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            logger.warning("Upload failed: Empty filename")
            return jsonify({"error": "No selected file"}), 400
        
        if file and file.filename.endswith(".pdf"):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            
            try:
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
                
                max_size = 10 * 1024 * 1024
                logger.info(f"File: {filename}, Size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
                
                if file_size > max_size:
                    logger.warning(f"Upload failed: File too large ({file_size / (1024*1024):.2f} MB)")
                    return jsonify({"error": f"File too large. Maximum size is {max_size // (1024*1024)}MB"}), 400
            except Exception as e:
                logger.warning(f"Could not determine file size: {e}")
            
            logger.info(f"Saving file to: {path}")
            file.save(path)
            logger.info(f"File saved successfully")
            
            import gc
            gc.collect()
            gc.collect()
            
            try:
                import psutil
                process = psutil.Process()
                mem_before = process.memory_info().rss / 1024 / 1024
                logger.info(f"Memory before processing: {mem_before:.2f} MB")
            except ImportError:
                logger.info("psutil not available for memory monitoring")
            except Exception as e:
                logger.warning(f"Could not check memory: {e}")
            
            try:
                logger.info(f"Starting PDF processing for: {filename}")
                processing_start = datetime.now()
                upload_elapsed = (processing_start - upload_start_time).total_seconds()
                logger.info(f"Time elapsed before processing: {upload_elapsed:.2f} seconds")
                
                data = process_pdf(path)
                
                processing_time = (datetime.now() - processing_start).total_seconds()
                total_elapsed = (datetime.now() - upload_start_time).total_seconds()
                logger.info(f"PDF processing completed in {processing_time:.2f} seconds")
                logger.info(f"Total request time so far: {total_elapsed:.2f} seconds")
                
                if data:
                    logger.info(f"Data extracted successfully. Keys: {list(data.keys())}")
                else:
                    logger.warning(f"process_pdf returned None for: {filename}")
                    
            except GeminiQuotaExceededError as e:
                logger.error(f"GEMINI QUOTA EXCEEDED for {filename}: {e.message}")
                logger.error(traceback.format_exc())
                
                api_message = e.message
                
                if e.is_daily_limit:
                    user_message = api_message if api_message else "Daily AI request limit reached."
                    if "tomorrow" not in user_message.lower() and "reset" not in user_message.lower():
                        user_message = f"{user_message} Please try again tomorrow."
                    return jsonify({
                        "error": "Daily AI request limit reached",
                        "message": user_message,
                        "api_message": api_message
                    }), 429
                else:
                    if e.retry_after and e.retry_after < 60:
                        retry_minutes = max(1, int(e.retry_after / 60))
                        retry_msg = f" Please try again in {retry_minutes} minute{'s' if retry_minutes > 1 else ''}."
                    elif e.retry_after:
                        retry_msg = f" Please try again in {int(e.retry_after)} seconds."
                    else:
                        retry_msg = " Please try again in a few moments."
                    
                    user_message = api_message if api_message else "AI request rate limit reached."
                    return jsonify({
                        "error": "AI request rate limit reached",
                        "message": f"{user_message}{retry_msg}",
                        "api_message": api_message
                    }), 429
            except GeminiAPIError as e:
                logger.error(f"GEMINI API ERROR for {filename}: {e.message} (status: {e.status_code}, code: {e.error_code})")
                logger.error(traceback.format_exc())
                return jsonify({
                    "error": "Extraction failed: API error",
                    "message": e.message
                }), e.status_code or 502
            except GeminiAPIDisabledError as e:
                logger.warning(f"GEMINI API DISABLED for {filename}: {e.message}")
                return jsonify({
                    "error": "Extraction failed: API disabled",
                    "message": "The AI service is currently disabled. Please contact support or enable it in configuration."
                }), 503
            except MemoryError as e:
                logger.error(f"MEMORY ERROR during PDF processing for {filename}: {e}")
                logger.error(traceback.format_exc())
                return jsonify({
                    "error": "Extraction failed: Out of memory",
                    "message": "The PDF is too large or complex to process. Please try a smaller file or contact support."
                }), 500
            except TimeoutError as e:
                logger.error(f"TIMEOUT ERROR during PDF processing for {filename}: {e}")
                logger.error(traceback.format_exc())
                return jsonify({
                    "error": "Extraction failed: Request timeout",
                    "message": "The processing took too long. Please try again or use a smaller PDF file."
                }), 504
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e).lower()
                
                if 'timeout' in error_msg or 'Timeout' in error_type:
                    logger.error(f"TIMEOUT ERROR during PDF processing for {filename}: {e}")
                    logger.error(traceback.format_exc())
                    return jsonify({
                        "error": "Extraction failed: API timeout",
                        "message": "The AI service took too long to respond. Please try again."
                    }), 504
                else:
                    logger.error(f"UNEXPECTED EXCEPTION during PDF processing for {filename}")
                    logger.error(f"Exception type: {error_type}")
                    logger.error(f"Exception message: {str(e)}")
                    logger.error(traceback.format_exc())
                    return jsonify({
                        "error": "Extraction failed: Unexpected error",
                        "message": f"An unexpected error occurred: {str(e)}"
                    }), 500
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
                logger.error(f"No data returned from process_pdf for {filename}")
                if Config.TEST_MODE:
                    return jsonify({
                        "error": "Extraction failed: Test mode mock data generation failed",
                        "message": "The test data generation encountered an error. Please check the logs."
                    }), 500
                else:
                    return jsonify({
                        "error": "Extraction failed: No data returned",
                        "message": "The AI service did not return any data. This may be due to API errors, quota limits, or processing issues. Please try again or contact support."
                    }), 502

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
                            
                            clean_name = normalize_name(clean_name)
                            
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
                            
                            actor = normalize_name(actor)
                            
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
                 
                 clean_name = normalize_name(clean_name)
                 
                 all_credits.append({
                     'cat': 'Ensemble',
                     'role': 'Ensemble',
                     'actor': clean_name,
                     'is_equity': is_eq
                 })

            if not isinstance(data, dict):
                print(f"Error: data is not a dictionary, type: {type(data)}")
                return jsonify({"error": "Invalid data format returned from extraction"}), 500
            
            data['all_credits'] = all_credits
            
            required_fields = ['show_title', 'theatre_name', 'production_year']
            for field in required_fields:
                if field not in data:
                    data[field] = data.get(field, '')
            
            try:
                logger.info("Rendering review template")
                return render_template("review.html", data=data, filename=filename)
            except Exception as e:
                logger.error(f"TEMPLATE RENDERING ERROR: {e}")
                logger.error(traceback.format_exc())
                logger.error(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return jsonify({
                    "error": "Failed to render review page",
                    "message": f"An error occurred while displaying the results: {str(e)}"
                }), 500
        
        return jsonify({"error": "Invalid file type"}), 400
        
    except MemoryError as e:
        logger.error(f"MEMORY ERROR in upload route: {e}")
        logger.error(traceback.format_exc())
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except:
                pass
        return jsonify({
            "error": "Upload failed: Out of memory",
            "message": "The server ran out of memory processing your request. Please try a smaller file."
        }), 500
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        logger.error(f"UNHANDLED EXCEPTION in upload route")
        logger.error(f"Exception type: {error_type}")
        logger.error(f"Exception message: {error_msg}")
        logger.error(traceback.format_exc())
        
        upload_duration = (datetime.now() - upload_start_time).total_seconds()
        logger.info(f"Upload request failed after {upload_duration:.2f} seconds")
        logger.info("=" * 80)
        
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except Exception as cleanup_error:
                logger.warning(f"Could not clean up file {path}: {cleanup_error}")
        
        return jsonify({
            "error": f"Upload failed: {error_type}",
            "message": f"An unexpected error occurred: {error_msg}"
        }), 500
    finally:
        upload_duration = (datetime.now() - upload_start_time).total_seconds()
        logger.info(f"Upload request completed in {upload_duration:.2f} seconds")
        logger.info("=" * 80)

@app.route("/dashboard")
@login_required
def dashboard():
    productions = Production.query.order_by(Production.id.desc()).all()
    return render_template("dashboard.html", productions=productions)

@app.route("/settings")
@login_required
def settings():
    try:
        admin_settings = AdminSettings.query.first()
        if not admin_settings:
            admin_settings = AdminSettings.get_or_create()
        return render_template("settings.html", admin_settings=admin_settings)
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        try:
            admin_settings = AdminSettings.get_or_create()
            return render_template("settings.html", admin_settings=admin_settings)
        except Exception as e2:
            logger.error(f"Error creating admin settings: {e2}")
            from werkzeug.security import generate_password_hash
            admin_settings = AdminSettings(
                username='admin',
                password_hash=generate_password_hash('admin')
            )
            db.session.add(admin_settings)
            db.session.commit()
            return render_template("settings.html", admin_settings=admin_settings)

@app.route("/settings/update-credentials", methods=["POST"])
@login_required
def update_credentials():
    try:
        data = request.json
        new_username = data.get("username", "").strip()
        current_password = data.get("current_password", "")
        new_password = data.get("new_password", "")
        confirm_password = data.get("confirm_password", "")
        
        if not new_username:
            return jsonify({"error": "Username cannot be empty"}), 400
        
        admin_settings = AdminSettings.query.first()
        if not admin_settings:
            admin_settings = AdminSettings.get_or_create()
        
        if new_password:
            if not current_password:
                return jsonify({"error": "Current password is required to change password"}), 400
            
            if not check_password_hash(admin_settings.password_hash, current_password):
                try:
                    if current_password != Config.ADMIN_PASSWORD:
                        return jsonify({"error": "Current password is incorrect"}), 400
                except:
                    return jsonify({"error": "Current password is incorrect"}), 400
            
            if len(new_password) < 6:
                return jsonify({"error": "New password must be at least 6 characters long"}), 400
            
            if new_password != confirm_password:
                return jsonify({"error": "New password and confirm password do not match"}), 400
            
            admin_settings.password_hash = generate_password_hash(new_password)
        
        admin_settings.username = new_username
        db.session.commit()
        
        return jsonify({"success": True, "message": "Credentials updated successfully."})
    except Exception as e:
        logger.error(f"Error updating credentials: {e}")
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/edit/<int:id>")
@login_required
def edit(id):
    production = db.session.get(Production, id)
    if not production:
        return "Production not found", 404
    if not production.theater.joomla_id:
        return "Theater is not linked to Joomla database", 400
        
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
        "theatre_name": get_theater_name_from_joomla(production.theater.joomla_id),
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
@login_required
def save():
    try:
        from joomla_sync import sync_theaters_from_joomla
        sync_count = sync_theaters_from_joomla()
        if sync_count > 0:
            logger.info(f"Auto-synced {sync_count} theaters from Joomla before save")
    except Exception as e:
        logger.warning(f"Could not auto-sync theaters: {e}")
    
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
        theater = find_or_match_theater(theater_name)
        
        if not theater:
            return jsonify({
                "error": "Theater not found",
                "message": f"Theater '{theater_name}' was not found in the database. Please sync theaters from Joomla first, or ensure the theater name matches exactly.",
                "suggested_action": "sync_theaters"
            }), 400
        
        if not theater.joomla_id:
            return jsonify({
                "error": "Theater not linked to Joomla",
                "message": f"Theater '{theater.name}' exists but is not linked to Joomla database. Please sync theaters from the admin dashboard.",
                "suggested_action": "sync_theaters"
            }), 400

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

            normalized_name = normalize_name(actor_name)
            person = Person.query.filter(Person.name.ilike(normalized_name)).first()
            if not person:
                person = Person(name=normalized_name, disciplines=category)
                db.session.add(person)
                db.session.flush()
            elif person.name != normalized_name:
                person.name = normalized_name
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
@login_required
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
@login_required
def download_production(id):
    try:
        production = db.session.get(Production, id)
        if not production:
            return "Production not found", 404
        if not production.theater.joomla_id:
            return "Theater is not linked to Joomla database", 400

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
            "theatre_name": get_theater_name_from_joomla(production.theater.joomla_id),
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

@app.route("/upload_person_photo/<int:id>", methods=["POST"])
@login_required
def upload_person_photo(id):
    person = db.session.get(Person, id)
    if not person:
        return jsonify({"error": "Person not found"}), 404
    
    if "photo" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["photo"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
        return jsonify({"error": "Invalid file type. Please upload an image file."}), 400
    
    try:
        profiles_dir = os.path.join("static", "profiles")
        os.makedirs(profiles_dir, exist_ok=True)
        
        img = Image.open(file.stream)
        
        target_width = 200
        target_height = 300
        target_ratio = target_width / target_height
        
        img_width, img_height = img.size
        img_ratio = img_width / img_height
        
        if img_ratio > target_ratio:
            new_height = target_height
            new_width = int(new_height * img_ratio)
            left = (new_width - target_width) // 2
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img = img.crop((left, 0, left + target_width, target_height))
        else:
            new_width = target_width
            new_height = int(new_width / img_ratio)
            top = (new_height - target_height) // 2
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img = img.crop((0, top, target_width, top + target_height))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        filename = f"person_{id}.jpg"
        filepath = os.path.join(profiles_dir, filename)
        img.save(filepath, "JPEG", quality=90)
        
        photo_path = f"profiles/{filename}"
        person.photo = photo_path
        db.session.commit()
        
        photo_url = flask_url_for('static', filename=photo_path)
        if APPLICATION_ROOT != '/':
            root = APPLICATION_ROOT.rstrip('/')
            if not photo_url.startswith(root):
                photo_url = root + photo_url
        return jsonify({"success": True, "photo_url": photo_url})
    
    except Exception as e:
        logger.error(f"Error uploading person photo: {e}")
        logger.error(traceback.format_exc())
        db.session.rollback()
        return jsonify({"error": f"Failed to process image: {str(e)}"}), 500

@app.route("/admin/merge-duplicate-persons")
@login_required
def merge_duplicate_persons():
    try:
        from sqlalchemy import func
        
        all_persons = Person.query.all()
        name_groups = {}
        
        for person in all_persons:
            normalized = normalize_name(person.name)
            if normalized not in name_groups:
                name_groups[normalized] = []
            name_groups[normalized].append(person)
        
        merged_count = 0
        for normalized_name, persons in name_groups.items():
            if len(persons) > 1:
                primary = persons[0]
                primary.name = normalized_name
                
                for duplicate in persons[1:]:
                    Credit.query.filter_by(person_id=duplicate.id).update({'person_id': primary.id})
                    db.session.delete(duplicate)
                    merged_count += 1
        
        db.session.commit()
        return jsonify({"success": True, "message": f"Merged {merged_count} duplicate persons"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

def get_discipline_from_credit(category, role):
    category_map = {
        'Cast': 'Actor',
        'Musician': 'Musician',
        'Crew': 'Crew',
        'Swings': 'Swings',
        'Understudies': 'Understudies',
        'Dance Captain': 'Dance Captain',
        'Ensemble': 'Ensemble'
    }
    
    if category in category_map:
        return category_map[category]
    
    if category == 'Creative':
        role_lower = role.lower()
        if 'directed' in role_lower or 'director' in role_lower:
            return 'Director'
        elif 'choreographed' in role_lower or 'choreographer' in role_lower:
            return 'Choreographer'
        elif 'written' in role_lower or 'writer' in role_lower or 'book' in role_lower:
            return 'Writer'
        elif 'produced' in role_lower or 'producer' in role_lower:
            return 'Producer'
        elif 'lighting' in role_lower:
            return 'Lighting Designer'
        elif 'sound' in role_lower:
            return 'Sound Designer'
        elif 'costume' in role_lower:
            return 'Costume Designer'
        elif 'set' in role_lower or 'scenic' in role_lower:
            return 'Set Designer'
        elif 'designed' in role_lower or 'designer' in role_lower:
            return 'Designer'
        else:
            return 'Creative'
    
    return category

@app.route("/public/actor/<int:id>")
def public_actor(id):
    person = db.session.get(Person, id)
    if not person:
        return "Actor not found", 404
    
    normalized_name = normalize_name(person.name)
    if person.name != normalized_name:
        person.name = normalized_name
        db.session.commit()
    
    duplicate_person_ids = [p.id for p in Person.query.filter(Person.name.ilike(normalized_name)).all()]
    
    credits_query = db.session.query(Credit, Production, Show, Theater).join(
        Production, Credit.production_id == Production.id
    ).join(
        Show, Production.show_id == Show.id
    ).join(
        Theater, Production.theater_id == Theater.id
    ).filter(
        Credit.person_id.in_(duplicate_person_ids)
    ).order_by(Production.year.desc(), Show.title)
    
    all_credits = credits_query.all()
    
    credits_by_discipline = {}
    theaters_set = set()
    disciplines_set = set()
    
    for credit, production, show, theater in all_credits:
        discipline = credit.category
        if discipline not in credits_by_discipline:
            credits_by_discipline[discipline] = []
        
        if not theater.joomla_id:
            raise ValueError(f"Theater {theater.id} is not linked to Joomla")
        
        theater_name = get_theater_name_from_joomla(theater.joomla_id)
        
        from joomla_theater_fetch import get_theater_from_joomla
        joomla_data = get_theater_from_joomla(theater.joomla_id)
        if not joomla_data:
            raise ValueError(f"Theater data not found in Joomla for joomla_id: {theater.joomla_id}")
        
        theater_lat = joomla_data.get('latitude')
        theater_lng = joomla_data.get('longitude')
        theater_city = joomla_data.get('city')
        theater_state = joomla_data.get('state')
        
        credits_by_discipline[discipline].append({
            'role': credit.role,
            'show_title': show.title,
            'show_id': show.id,
            'theater_name': theater_name,
            'theater_id': theater.id,
            'year': production.year,
            'is_equity': credit.is_equity,
            'production_id': production.id
        })
        
        discipline_name = get_discipline_from_credit(credit.category, credit.role)
        disciplines_set.add(discipline_name)
        
        theaters_set.add((theater.id, theater_name, theater_lat, theater_lng, theater_city, theater_state))
    
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
    disciplines_list = sorted(disciplines_set)
    disciplines_count = len(disciplines_list)
    
    return render_template("public_actor.html", 
                         person=person, 
                         credits_by_discipline=credits_by_discipline,
                         theaters=theaters_list,
                         theaters_map=theaters_with_coords,
                         total_credits=total_credits,
                         disciplines_count=disciplines_count,
                         disciplines_list=disciplines_list)

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
        
        theater = prod.theater
        if not theater.joomla_id:
            raise ValueError(f"Theater {theater.id} is not linked to Joomla")
        theater_name = get_theater_name_from_joomla(theater.joomla_id)
        
        class TheaterWrapper:
            def __init__(self, theater_obj, name):
                self.id = theater_obj.id
                self.name = name
                self.joomla_id = theater_obj.joomla_id
        
        theater_wrapper = TheaterWrapper(theater, theater_name)
        
        all_credits_by_production[prod.id] = {
            'production': prod,
            'theater': theater_wrapper,
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
    
    if not theater.joomla_id:
        return "Theater not linked to Joomla database", 404
    
    from joomla_theater_fetch import get_theater_from_joomla
    joomla_theater_data = get_theater_from_joomla(theater.joomla_id)
    
    if not joomla_theater_data:
        return "Theater data not found in Joomla database", 404
    
    class TheaterData:
        def __init__(self, local_theater, joomla_data):
            self.id = local_theater.id
            self.joomla_id = joomla_data.get('joomla_id')
            self.name = joomla_data.get('name')
            self.address = joomla_data.get('address')
            self.description = joomla_data.get('description')
            self.image = joomla_data.get('image')
            self.latitude = joomla_data.get('latitude')
            self.longitude = joomla_data.get('longitude')
            self.city = joomla_data.get('city')
            self.state = joomla_data.get('state')
    
    theater_data = TheaterData(theater, joomla_theater_data)
    
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
                         theater=theater_data, 
                         shows_data=shows_data)

@app.route("/admin/add-sample-data")
@login_required
def add_sample_data_route():
    try:
        from add_sample_data import add_sample_data
        add_sample_data()
        return jsonify({"success": True, "message": "Sample data added successfully!"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/admin/sync-theaters")
@login_required
def sync_theaters_route():
    try:
        from joomla_sync import sync_theaters_from_joomla
        synced_count = sync_theaters_from_joomla()
        return jsonify({"success": True, "message": f"Synced {synced_count} theaters from Joomla database"}), 200
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
            
            person_credits_map = {}
            for person in persons:
                normalized_name = normalize_name(person.name)
                if normalized_name not in person_credits_map:
                    person_credits_map[normalized_name] = {
                        'person': person,
                        'ids': set([person.id])
                    }
                else:
                    person_credits_map[normalized_name]['ids'].add(person.id)
            
            for normalized_name, data in person_credits_map.items():
                all_person_ids = list(data['ids'])
                credits_query = Credit.query.filter(Credit.person_id.in_(all_person_ids))
                if is_category_filter:
                    credits_query = credits_query.filter(Credit.category.ilike(filter_type))

                if equity_filter == 'equity':
                    credits_query = credits_query.filter_by(is_equity=True)
                elif equity_filter == 'non-equity':
                    credits_query = credits_query.filter_by(is_equity=False)
                
                filtered_credits_count = credits_query.count()

                if filtered_credits_count > 0:
                    results['actors'].append({
                        'id': data['person'].id,
                        'name': normalized_name,
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
                Theater.joomla_id.isnot(None)
            ).all()
            
            for theater in theaters:
                try:
                    theater_name = get_theater_name_from_joomla(theater.joomla_id)
                    if query.lower() not in (theater_name or '').lower():
                        continue
                    
                    prod_count = Production.query.filter_by(theater_id=theater.id).count()
                    if prod_count > 0:
                        results['theaters'].append({
                            'id': theater.id,
                            'name': theater_name,
                            'productions_count': prod_count
                        })
                except:
                    continue
    
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
@login_required
def edit_understudies(production_id):
    data = request.json
    understudies = data.get("understudies", [])

    try:
        production = db.session.get(Production, production_id)
        if not production:
            return jsonify({"error": "Production not found"}), 404

        Credit.query.filter_by(production_id=production.id, category="Understudies").delete()

        for name in understudies:
            normalized_name = normalize_name(name)
            person = Person.query.filter(Person.name.ilike(normalized_name)).first()
            if not person:
                person = Person(name=normalized_name, disciplines="Understudies")
                db.session.add(person)
                db.session.flush()
            elif person.name != normalized_name:
                person.name = normalized_name
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