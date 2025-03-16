from flask import Flask
from threading import Thread
import logging
import socket
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return False
        except socket.error:
            return True

def run():
    retries = 3
    port = 5000

    while retries > 0:
        if not is_port_in_use(port):
            try:
                logger.info(f"Starting Flask server on port {port}...")
                app.run(host='0.0.0.0', port=port)
                break
            except Exception as e:
                logger.error(f"Failed to start Flask server: {e}")
                raise
        else:
            logger.warning(f"Port {port} is in use, waiting before retry...")
            time.sleep(2)
            retries -= 1

    if retries == 0:
        logger.error("Could not start Flask server after multiple attempts")
        raise RuntimeError("Failed to start Flask server due to port conflicts")

def keep_alive():
    logger.info("Initializing keep_alive server...")
    t = Thread(target=run)
    t.daemon = True  # This ensures the thread will be stopped when the main program exits
    t.start()
    logger.info("Keep_alive server initialized successfully")