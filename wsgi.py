import logging
import sys
from app import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('wsgi.log')
    ]
)

if __name__ == "__main__":
    app.run()
