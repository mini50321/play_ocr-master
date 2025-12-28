import os
import json
import base64
import requests
import fitz
import time
from dotenv import load_dotenv
from config import Config

load_dotenv()

def get_gemini_key():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return key

try:
    API_KEY = get_gemini_key()
except ValueError as e:
    print(f"Error loading API key: {e}")
    API_KEY = None

if API_KEY:
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
else:
    API_URL = None

def get_mock_data(pdf_path):
    filename = os.path.basename(pdf_path).lower()
    
    if "phantom" in filename:
        return {
            "show_title": "The Phantom of the Opera",
            "theatre_name": "The Gateway",
            "production_year": 2024,
            "dates": "January 15 - March 15, 2024",
            "cast": [
                {"role": "Phantom", "actor": "John Smith", "is_equity": True},
                {"role": "Christine Daaé", "actor": "Sarah Johnson", "is_equity": True},
                {"role": "Raoul", "actor": "Michael Brown", "is_equity": False},
                {"role": "Carlotta", "actor": "Emily Davis", "is_equity": True},
                {"role": "Madame Giry", "actor": "Lisa Anderson", "is_equity": True},
                {"role": "Meg Giry", "actor": "Jennifer Martinez", "is_equity": False},
                {"role": "André", "actor": "Robert Taylor", "is_equity": False},
                {"role": "Firmin", "actor": "David Wilson", "is_equity": True}
            ],
            "creative": [
                {"role": "Director", "actor": "David Wilson", "is_equity": True},
                {"role": "Music Director", "actor": "Robert Taylor", "is_equity": True},
                {"role": "Choreographer", "actor": "Michael Brown", "is_equity": False},
                {"role": "Set Designer", "actor": "Jennifer Martinez", "is_equity": True},
                {"role": "Lighting Designer", "actor": "Emily Davis", "is_equity": False},
                {"role": "Costume Designer", "actor": "Sarah Johnson", "is_equity": True}
            ],
            "musicians": [
                {"role": "Piano", "actor": "Musician One", "is_equity": True},
                {"role": "Violin", "actor": "Musician Two", "is_equity": False},
                {"role": "Cello", "actor": "Musician Three", "is_equity": True}
            ],
            "crew": [
                {"role": "Stage Manager", "actor": "Crew Member One", "is_equity": True},
                {"role": "Assistant Stage Manager", "actor": "Crew Member Two", "is_equity": False},
                {"role": "Sound Engineer", "actor": "Crew Member Three", "is_equity": False},
                {"role": "Props Master", "actor": "Crew Member Four", "is_equity": True}
            ],
            "ensemble": [
                "Ensemble Member One",
                "Ensemble Member Two",
                "Ensemble Member Three",
                "Ensemble Member Four",
                "Ensemble Member Five"
            ],
            "swings": [
                "Swing One",
                "Swing Two"
            ],
            "understudies": [
                "Understudy One",
                "Understudy Two"
            ],
            "dance_captains": [
                "Dance Captain Name"
            ]
        }
    elif "christmas" in filename:
        return {
            "show_title": "A Christmas Carol",
            "theatre_name": "John W. Engeman Theater",
            "production_year": 2024,
            "dates": "November 20 - December 30, 2024",
            "cast": [
                {"role": "Ebenezer Scrooge", "actor": "Sarah Johnson", "is_equity": True},
                {"role": "Ghost of Christmas Past", "actor": "Emily Davis", "is_equity": True},
                {"role": "Ghost of Christmas Present", "actor": "John Smith", "is_equity": True},
                {"role": "Ghost of Christmas Yet to Come", "actor": "Michael Brown", "is_equity": False},
                {"role": "Bob Cratchit", "actor": "Lisa Anderson", "is_equity": False},
                {"role": "Tiny Tim", "actor": "Robert Taylor", "is_equity": False},
                {"role": "Mrs. Cratchit", "actor": "Jennifer Martinez", "is_equity": True},
                {"role": "Nephew Fred", "actor": "David Wilson", "is_equity": True}
            ],
            "creative": [
                {"role": "Director", "actor": "David Wilson", "is_equity": True},
                {"role": "Music Director", "actor": "Robert Taylor", "is_equity": True},
                {"role": "Choreographer", "actor": "Emily Davis", "is_equity": False}
            ],
            "musicians": [
                {"role": "Piano", "actor": "Musician A", "is_equity": True},
                {"role": "Violin", "actor": "Musician B", "is_equity": False}
            ],
            "crew": [
                {"role": "Stage Manager", "actor": "Stage Manager Name", "is_equity": True},
                {"role": "Sound Designer", "actor": "Sound Designer Name", "is_equity": False}
            ],
            "ensemble": [
                "Ensemble A",
                "Ensemble B",
                "Ensemble C"
            ],
            "swings": [
                "Swing A"
            ],
            "understudies": [
                "Understudy A",
                "Understudy B"
            ],
            "dance_captains": []
        }
    elif "grease" in filename:
        return {
            "show_title": "Grease",
            "theatre_name": "THE ARGYLE THEATRE",
            "production_year": 2023,
            "dates": "June 1 - August 31, 2023",
            "cast": [
                {"role": "Danny Zuko", "actor": "John Smith", "is_equity": True},
                {"role": "Sandy Dumbrowski", "actor": "Emily Davis", "is_equity": True},
                {"role": "Betty Rizzo", "actor": "Robert Taylor", "is_equity": False},
                {"role": "Kenickie", "actor": "Michael Brown", "is_equity": True},
                {"role": "Frenchy", "actor": "Sarah Johnson", "is_equity": False},
                {"role": "Marty", "actor": "Lisa Anderson", "is_equity": True},
                {"role": "Jan", "actor": "Jennifer Martinez", "is_equity": False},
                {"role": "Doody", "actor": "David Wilson", "is_equity": False},
                {"role": "Roger", "actor": "Robert Taylor", "is_equity": True},
                {"role": "Sonny", "actor": "Michael Brown", "is_equity": False}
            ],
            "creative": [
                {"role": "Director", "actor": "Jennifer Martinez", "is_equity": True},
                {"role": "Music Director", "actor": "David Wilson", "is_equity": True},
                {"role": "Choreographer", "actor": "Emily Davis", "is_equity": True}
            ],
            "musicians": [
                {"role": "Guitar", "actor": "Guitarist Name", "is_equity": True},
                {"role": "Bass", "actor": "Bassist Name", "is_equity": False},
                {"role": "Drums", "actor": "Drummer Name", "is_equity": True},
                {"role": "Keyboard", "actor": "Keyboardist Name", "is_equity": False}
            ],
            "crew": [
                {"role": "Stage Manager", "actor": "SM Name", "is_equity": True},
                {"role": "Lighting Designer", "actor": "LD Name", "is_equity": True},
                {"role": "Sound Engineer", "actor": "SE Name", "is_equity": False}
            ],
            "ensemble": [
                "Ensemble 1",
                "Ensemble 2",
                "Ensemble 3",
                "Ensemble 4"
            ],
            "swings": [
                "Swing 1",
                "Swing 2"
            ],
            "understudies": [
                "Understudy 1"
            ],
            "dance_captains": [
                "Dance Captain"
            ]
        }
    else:
        return {
            "show_title": "Sample Show",
            "theatre_name": "THE ARGYLE THEATRE",
            "production_year": 2024,
            "dates": "January 1 - December 31, 2024",
            "cast": [
                {"role": "Lead Role", "actor": "John Smith", "is_equity": True},
                {"role": "Supporting Role", "actor": "Sarah Johnson", "is_equity": False}
            ],
            "creative": [
                {"role": "Director", "actor": "David Wilson", "is_equity": True}
            ],
            "musicians": [],
            "crew": [],
            "ensemble": [],
            "swings": [],
            "understudies": [],
            "dance_captains": []
        }

def get_pdf_images(pdf_path):
    images = []
    doc = None
    try:
        doc = fitz.open(pdf_path)
        max_pages = 10
        page_count = min(len(doc), max_pages)
        
        for page_num in range(page_count):
            try:
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_bytes = pix.tobytes("jpeg")
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                images.append(b64_img)
                pix = None
                page = None
            except Exception as e:
                print(f"Error processing page {page_num}: {e}")
                continue
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if doc:
            doc.close()
            doc = None
    return images

def process_pdf(pdf_path):
    if Config.TEST_MODE:
        print(f"TEST MODE: Using mock data for {pdf_path}")
        data = get_mock_data(pdf_path)
        
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            preview_dir = os.path.join(base_dir, "static", "previews")
            os.makedirs(preview_dir, exist_ok=True)
            
            dataset_name = os.path.splitext(os.path.basename(pdf_path))[0]
            preview_filename = f"{dataset_name}_preview.jpg"
            preview_full_path = os.path.join(preview_dir, preview_filename)
            
            if os.path.exists(preview_full_path):
                data['preview_image'] = f"previews/{preview_filename}"
        except Exception as e:
            print(f"Error handling preview in test mode: {e}")
        
        return data
    
    if not API_KEY or not API_URL:
        print("API Key or API URL missing.")
        return None

    print(f"Processing {pdf_path}...")
    images = get_pdf_images(pdf_path)
    
    if not images:
        print(f"No content found for {pdf_path}")
        return None

    preview_image_path = None
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        preview_dir = os.path.join(base_dir, "static", "previews")
        os.makedirs(preview_dir, exist_ok=True)
        
        dataset_name = os.path.splitext(os.path.basename(pdf_path))[0]
        preview_filename = f"{dataset_name}_preview.jpg"
        preview_full_path = os.path.join(preview_dir, preview_filename)
        
        if images:
            with open(preview_full_path, "wb") as f:
                f.write(base64.b64decode(images[0]))
            preview_image_path = f"previews/{preview_filename}"
            
    except Exception as e:
        print(f"Error saving preview image: {e}")

    prompt_text = """
    You are an expert at extracting structured data from theatre playbills.
    Analyze the provided images of a playbill. Extract the following information in strict JSON format:
    
    {
      "show_title": "Title of the show",
      "theatre_name": "Name of the theatre",
      "production_year": 2025 (or extracted year as integer),
      "dates": "Performance dates range as string",
      "cast": [
        {"role": "Role Name", "actor": "Actor Name", "is_equity": boolean},
        ...
      ],
      "creative": [
         {"role": "Role Name (e.g. Director)", "actor": "Person Name", "is_equity": boolean},
         ...
      ],
      "musicians": [
         {"role": "Instrument", "actor": "Musician Name", "is_equity": boolean},
         ...
      ],
      "crew": [
         {"role": "Job Title", "actor": "Person Name", "is_equity": boolean},
         ...
      ],
      "ensemble": [
         "Actor Name 1", "Actor Name 2", ...
      ],
      "swings": [
         "Actor Name 1", "Actor Name 2", ...
      ],
      "understudies": [
         "Actor Name 1", "Actor Name 2", ...
      ],
      "dance_captains": [
        "Actor Name 1", "Actor Name 2", ...
      ]
    }
    
    IMPORTANT RULES:
    1. **Equity Members**: If a person's name has an asterisk (*) or symbol indicating Actors' Equity Association, set "is_equity": true. Remove the symbol from the name string.
    2. **Dual Roles**: If you see roles like "Directed & Choreographed by" or "Written & Directed by", split them into TWO separate entries with the same actor name. For example, "Directed & Choreographed by John Smith" should become two entries: {"role": "Director", "actor": "John Smith"} and {"role": "Choreographer", "actor": "John Smith"}.
    3. **Ensemble Splitting**: If you see a block of names under "Ensemble" or "Chorus", split them into individual strings in the "ensemble" list. Do NOT group them in one string.
    4. **Swings & Understudies**: Extract these into their own separate lists.
    5. **Dance Captains**: Extract under "dance_captains" list.
    6. If a field is not found, use empty list [] or null.
    7. The output must be pure JSON without markdown formatting.
    """

    parts = [{"text": prompt_text}]
    for img_b64 in images:
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": img_b64
            }
        })

    payload = {
        "contents": [{
            "parts": parts
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    max_retries = 3
    for attempt in range(max_retries):
        response = None
        try:
            response = requests.post(
                API_URL, 
                json=payload, 
                headers={"Content-Type": "application/json"},
                timeout=(30, 120)
            )
            
            if response.status_code == 429:
                wait_time = (attempt + 1) * 5
                print(f"Rate limit hit. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
                
            response.raise_for_status()
            result = response.json()
            
            if not result.get('candidates') or len(result['candidates']) == 0:
                print("API returned no candidates")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
            
            if 'content' not in result['candidates'][0] or 'parts' not in result['candidates'][0]['content']:
                print("Unexpected API response structure")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
            
            content_text = result['candidates'][0]['content']['parts'][0]['text']
            content_text = content_text.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(content_text)
            if preview_image_path:
                data['preview_image'] = preview_image_path
            return data

        except requests.exceptions.Timeout:
            print(f"API request timeout (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None
        except requests.exceptions.RequestException as e:
            print(f"API request error (attempt {attempt + 1}/{max_retries}): {e}")
            if response:
                print(f"Status Code: {response.status_code}")
                try:
                    print(f"API Response: {response.text[:500]}")
                except:
                    pass
                
                if response.status_code == 400:
                    try:
                        error_data = response.json()
                        if 'error' in error_data and 'message' in error_data['error']:
                            error_msg = error_data['error']['message']
                            if 'location' in error_msg.lower() or 'region' in error_msg.lower():
                                print("Error: Gemini API region restriction")
                                return None
                    except:
                        pass
                        
            if response and response.status_code == 429:
                wait_time = (attempt + 1) * 5
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
            elif attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                import traceback
                traceback.print_exc()
                break
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"Error parsing API response (attempt {attempt + 1}/{max_retries}): {e}")
            if response:
                try:
                    print(f"Response text: {response.text[:500]}")
                except:
                    pass
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None
        except Exception as e:
            print(f"Unexpected error (attempt {attempt + 1}/{max_retries}): {e}")
            import traceback
            traceback.print_exc()
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            break
    
    return None
