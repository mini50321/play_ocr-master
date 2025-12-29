import os
import json
import base64
import requests
import fitz
import time
import logging
import traceback
import gc
from dotenv import load_dotenv
from config import Config

load_dotenv()

logger = logging.getLogger(__name__)

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
        logger.info(f"Opening PDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        
        file_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
        file_size_mb = file_size / (1024 * 1024)
        logger.info(f"PDF file size: {file_size_mb:.2f} MB")
        
        max_pages = 6 if file_size_mb > 3 else 8
        page_count = min(len(doc), max_pages)
        logger.info(f"Processing {page_count} pages from PDF (max {max_pages} pages, file size: {file_size_mb:.2f} MB)")
        
        for page_num in range(page_count):
            try:
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                img_bytes = pix.tobytes("jpeg", jpg_quality=75)
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                images.append(b64_img)
                
                del img_bytes
                del b64_img
                pix = None
                del pix
                page = None
                del page
                
                import gc
                gc.collect()
                
                logger.debug(f"Processed page {page_num + 1}/{page_count}")
            except MemoryError as e:
                logger.error(f"MEMORY ERROR processing page {page_num}: {e}")
                logger.error(traceback.format_exc())
                if page_num > 0:
                    logger.warning(f"Returning {len(images)} pages processed before memory error")
                    break
                raise
            except Exception as e:
                logger.warning(f"Error processing page {page_num}: {e}")
                logger.debug(traceback.format_exc())
                continue
        logger.info(f"Successfully processed {len(images)} pages")
    except MemoryError:
        logger.error(f"MEMORY ERROR processing PDF {pdf_path}")
        raise
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {e}")
        logger.error(traceback.format_exc())
        raise
    finally:
        if doc:
            doc.close()
            doc = None
        gc.collect()
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

    logger.info(f"Processing {pdf_path}...")
    try:
        images = get_pdf_images(pdf_path)
    except MemoryError as e:
        logger.error(f"MEMORY ERROR extracting images from PDF: {e}")
        logger.error(traceback.format_exc())
        return None
    except Exception as e:
        logger.error(f"Failed to extract images from PDF: {e}")
        logger.error(traceback.format_exc())
        return None
    
    if not images:
        logger.warning(f"No content found for {pdf_path}")
        return None
    
    logger.info(f"Extracted {len(images)} images, preparing API request...")
    
    total_image_size = sum(len(img.encode('utf-8')) for img in images)
    logger.info(f"Total base64 image data size: {total_image_size / (1024*1024):.2f} MB")

    preview_image_path = None
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        preview_dir = os.path.join(base_dir, "static", "previews")
        os.makedirs(preview_dir, exist_ok=True)
        
        dataset_name = os.path.splitext(os.path.basename(pdf_path))[0]
        preview_filename = f"{dataset_name}_preview.jpg"
        preview_full_path = os.path.join(preview_dir, preview_filename)
        
        if images:
            preview_data = base64.b64decode(images[0])
            with open(preview_full_path, "wb") as f:
                f.write(preview_data)
            del preview_data
            preview_image_path = f"previews/{preview_filename}"
            gc.collect()
            
    except Exception as e:
        logger.error(f"Error saving preview image: {e}")

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
    
    del images
    gc.collect()
    logger.info("Cleared images from memory, preparing API payload")

    payload = {
        "contents": [{
            "parts": parts
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }
    
    payload_size = len(json.dumps(payload))
    logger.info(f"API payload size: {payload_size / (1024*1024):.2f} MB")

    max_retries = 5
    api_start_time = time.time()
    for attempt in range(max_retries):
        response = None
        try:
            logger.info(f"Making API request (attempt {attempt + 1}/{max_retries})...")
            request_start = time.time()
            response = requests.post(
                API_URL, 
                json=payload, 
                headers={"Content-Type": "application/json"},
                timeout=(30, 90)
            )
            request_duration = time.time() - request_start
            logger.info(f"API request completed in {request_duration:.2f} seconds, status: {response.status_code}")
            
            if response.status_code == 429:
                wait_time = None
                quota_exceeded = False
                daily_limit = False
                
                try:
                    error_data = response.json()
                    logger.warning(f"Rate limit error details: {error_data}")
                    
                    error_obj = error_data.get('error', {})
                    error_message = error_obj.get('message', '')
                    
                    if 'quota' in error_message.lower() or 'Quota exceeded' in error_message:
                        quota_exceeded = True
                        if 'limit: 20' in error_message or 'FreeTier' in str(error_data):
                            daily_limit = True
                    
                    details = error_obj.get('details', [])
                    for detail in details:
                        if detail.get('@type') == 'type.googleapis.com/google.rpc.RetryInfo':
                            retry_delay = detail.get('retryDelay', '')
                            if retry_delay:
                                try:
                                    wait_time = int(retry_delay.replace('s', '').strip())
                                    logger.info(f"Found RetryInfo delay: {wait_time} seconds")
                                except (ValueError, AttributeError):
                                    pass
                    
                    if not wait_time and 'retry in' in error_message.lower():
                        import re
                        match = re.search(r'retry in ([\d.]+)s?', error_message, re.IGNORECASE)
                        if match:
                            try:
                                wait_time = int(float(match.group(1)) + 1)
                                logger.info(f"Extracted retry delay from message: {wait_time} seconds")
                            except (ValueError, AttributeError):
                                pass
                except Exception as e:
                    logger.warning(f"Could not parse rate limit error: {e}")
                
                if not wait_time:
                    wait_time = min(120, 10 * (2 ** attempt))
                    logger.warning(f"Using exponential backoff: {wait_time} seconds")
                else:
                    wait_time = min(300, wait_time)
                    logger.warning(f"Using API-suggested retry delay: {wait_time} seconds")
                
                if attempt < max_retries - 1:
                    if daily_limit:
                        logger.error("Daily quota limit reached (20 requests/day for free tier). Waiting before retry...")
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    if daily_limit:
                        logger.error("Daily quota limit exhausted (20 requests/day for free tier). Quota resets daily.")
                        return None
                    logger.error(f"Rate limit hit on final attempt. All retries exhausted.")
                    return None
                
            response.raise_for_status()
            result = response.json()
            
            if not result.get('candidates') or len(result['candidates']) == 0:
                logger.warning(f"API returned no candidates (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
            
            if 'content' not in result['candidates'][0] or 'parts' not in result['candidates'][0]['content']:
                logger.warning(f"Unexpected API response structure (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
            
            content_text = result['candidates'][0]['content']['parts'][0]['text']
            content_text = content_text.replace("```json", "").replace("```", "").strip()
            
            try:
                data = json.loads(content_text)
                if not isinstance(data, dict):
                    logger.error(f"Parsed data is not a dictionary: {type(data)} (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return None
                
                if preview_image_path:
                    data['preview_image'] = preview_image_path
                logger.info(f"Successfully parsed JSON data with keys: {list(data.keys())}")
                return data
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error (attempt {attempt + 1}/{max_retries}): {e}")
                logger.debug(f"Content text preview: {content_text[:200]}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None

        except requests.exceptions.Timeout as e:
            elapsed = time.time() - api_start_time
            logger.error(f"API REQUEST TIMEOUT after {elapsed:.2f} seconds (attempt {attempt + 1}/{max_retries}): {e}")
            logger.error(traceback.format_exc())
            if attempt < max_retries - 1:
                wait_time = min(5, 180 - elapsed - 10)
                if wait_time > 0:
                    logger.info(f"Waiting {wait_time:.1f} seconds before retry...")
                    time.sleep(wait_time)
                continue
            logger.error("API timeout: All retry attempts exhausted")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API REQUEST ERROR (attempt {attempt + 1}/{max_retries}): {e}")
            if response:
                logger.error(f"Status Code: {response.status_code}")
                try:
                    logger.error(f"API Response: {response.text[:500]}")
                except:
                    pass
                
                if response.status_code == 400:
                    try:
                        error_data = response.json()
                        if 'error' in error_data and 'message' in error_data['error']:
                            error_msg = error_data['error']['message']
                            if 'location' in error_msg.lower() or 'region' in error_msg.lower():
                                logger.error("Gemini API region restriction detected")
                                return None
                    except:
                        pass
                        
            if response and response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    try:
                        wait_time = int(retry_after)
                    except ValueError:
                        wait_time = min(120, 10 * (2 ** attempt))
                else:
                    wait_time = min(120, 10 * (2 ** attempt))
                
                if attempt < max_retries - 1:
                    logger.warning(f"Rate limit in exception handler. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error("Rate limit: All retry attempts exhausted in exception handler")
                    return None
            elif attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                logger.error(f"Max retries reached for API request. Last error: {e}")
                logger.error(traceback.format_exc())
                return None
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing API response structure (attempt {attempt + 1}/{max_retries}): {e}")
            logger.error(traceback.format_exc())
            if response:
                try:
                    logger.debug(f"Response text: {response.text[:500]}")
                except:
                    pass
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None
        except MemoryError as e:
            logger.error(f"MEMORY ERROR during API processing (attempt {attempt + 1}/{max_retries}): {e}")
            logger.error(traceback.format_exc())
            return None
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"UNEXPECTED ERROR (attempt {attempt + 1}/{max_retries}): {error_type} - {e}")
            logger.error(traceback.format_exc())
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None
    
    logger.error("All retry attempts exhausted. Returning None.")
    return None
