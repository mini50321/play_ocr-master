import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
    
    if DB_TYPE == 'mysql':
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_USER = os.getenv('DB_USER', 'root')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '')
        DB_NAME = os.getenv('DB_NAME', 'playbill')
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///playbill.db"
    
    UPLOAD_FOLDER = "uploads"
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    JOOMLA_DB_HOST = os.getenv('JOOMLA_DB_HOST', 'localhost')
    JOOMLA_DB_USER = os.getenv('JOOMLA_DB_USER', 'root')
    JOOMLA_DB_PASSWORD = os.getenv('JOOMLA_DB_PASSWORD', '')
    JOOMLA_DB_NAME = os.getenv('JOOMLA_DB_NAME', 'broadmain')
    JOOMLA_THEATER_TABLE = os.getenv('JOOMLA_THEATER_TABLE', 'wa8wx_jbusinessdirectory_companies')
    
    TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'
    
    GEMINI_API_ENABLED = os.getenv('GEMINI_API_ENABLED', 'false').lower() == 'true'
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', None)
    GEMINI_CLIENT_API_KEY = os.getenv('GEMINI_CLIENT_API_KEY', None)