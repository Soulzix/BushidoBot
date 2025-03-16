from flask import Flask
from threading import Thread
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    try:
        logger.info("Starting Flask server on port 5000...")
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Failed to start Flask server: {e}")
        raise

def keep_alive():
    logger.info("Initializing keep_alive server...")
    t = Thread(target=run)
    t.daemon = True  # This ensures the thread will be stopped when the main program exits
    t.start()
    logger.info("Keep_alive server initialized successfully")