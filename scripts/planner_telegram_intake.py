import os
import time
import json
import logging
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Check for required env vars
def check_env_vars():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars must be set.")
        exit(1)

# Setup logging
LOG_FILE = '/Users/sixx/.openclaw/workspace/planner/ui_reviews/intake.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='[%(asctime)s] %(message)s')

# Directories
INBOX_DIR = '/Users/sixx/.openclaw/workspace/planner/ui_reviews/inbox'

os.makedirs(INBOX_DIR, exist_ok=True)

# Telegram bot instance
bot = Bot(token=TELEGRAM_BOT_TOKEN)

last_update_id = None

def download_photo(file_id, dest_path):
    try:
        new_file = bot.get_file(file_id)
        file_path = new_file.file_path
        # Determine the file extension from the file path
        ext = os.path.splitext(file_path)[-1] or '.jpg'
        dest_file = os.path.join(dest_path, f'image{ext}')
        new_file.download(dest_file)
        return os.path.basename(dest_file)
    except TelegramError as e:
        logging.error(f"Failed to download photo: {e}")
        return None

def process_update(update):
    message = update.message
    if not message:
        return
    if str(message.chat_id) != TELEGRAM_CHAT_ID:
        return

    if not message.photo:
        return

    # Create batch folder
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    batch_id = f'review_{timestamp}'
    batch_path = os.path.join(INBOX_DIR, batch_id)
    images_path = os.path.join(batch_path, 'images')
    os.makedirs(images_path, exist_ok=True)

    # Download photos
    image_files = []
    for idx, photo_size in enumerate(message.photo):
        # Download highest resolution
        file_id = photo_size.file_id
        filename = download_photo(file_id, images_path)
        if filename:
            image_files.append(filename)

    # Metadata
    metadata = {
        'batch_id': batch_id,
        'source': 'telegram',
        'timestamp': datetime.utcnow().isoformat(),
        'caption': message.caption or '',
        'image_files': image_files
    }

    with open(os.path.join(batch_path, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)

    logging.info(f"Batch {batch_id} created with {len(image_files)} images")
    print(f"Batch {batch_id} created with {len(image_files)} images")


def main_loop():
    global last_update_id
    check_env_vars()
    while True:
        updates = bot.get_updates(offset=last_update_id, timeout=30)
        for update in updates:
            last_update_id = update.update_id + 1
            process_update(update)
        time.sleep(2)


if __name__ == '__main__':
    print("Starting Sixx Telegram screenshot intake listener...")
    main_loop()
