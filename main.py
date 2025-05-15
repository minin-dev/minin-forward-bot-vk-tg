# Copyright (c) 2023 [Eiztrips]
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import sys
import logging
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'app.log'), mode='a')
    ]
)
logger = logging.getLogger(__name__)

os.makedirs('logs', exist_ok=True)

def run_birthday_module():
    try:
        from src.modules.birthday.birthday_module import birthday
        birthday()
    except Exception as e:
        logger.error(f"Error in birthday module: {e}")

def run_event_module():
    try:
        from src.modules.event.event_module import main as event_main
        event_main()
    except Exception as e:
        logger.error(f"Error in event module: {e}")

if __name__ == "__main__":
    logger.info("Starting VK to TG forwarding system")
    
    birthday_thread = threading.Thread(target=run_birthday_module)
    event_thread = threading.Thread(target=run_event_module)
    
    birthday_thread.daemon = True
    event_thread.daemon = True
    
    birthday_thread.start()
    event_thread.start()
    
    try:
        birthday_thread.join()
        event_thread.join()
    except KeyboardInterrupt:
        logger.info("Application shutdown requested")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    
    logger.info("Application shutting down")
