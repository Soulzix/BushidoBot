from flask import Flask
from threading import Thread
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    try:
        # Use port 8080 which is standard for Replit
        port = int(os.getenv("PORT", 8080))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Failed to start keep-alive server: {e}")

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    logger.info("Keep alive server started")