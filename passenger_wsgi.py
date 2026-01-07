import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

try:
    from app import app
    application = app
except Exception as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    logging.error(f"Error loading application: {e}")
    import traceback
    logging.error(traceback.format_exc())
    raise

