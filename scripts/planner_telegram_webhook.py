import os
import json
import logging
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import base64
from io import BytesIO
import requests

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PORT = int(os.getenv('PORT', '8766'))

INBOX_DIR = '/Users/sixx/.openclaw/workspace/planner/ui_reviews/inbox'
LOG_FILE = '/Users/sixx/.openclaw/workspace/planner/ui_reviews/intake.log'

os.makedirs(INBOX_DIR, exist_ok=True)

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='[%(asctime)s] %(message)s')

class WebhookHandler(BaseHTTPRequestHandler):
    def _set_response(self, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def log_message(self, format, *args):
        # Override to prevent default stdout logging
        return

    def do_POST(self):
        if self.path != '/telegram-webhook':
            self._set_response(404)
            return

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            update = json.loads(post_data)
        except Exception as e:
            logging.error(f"Invalid JSON received: {e}")
            self._set_response(400)
            return

        message = update.get('message') or update.get('edited_message')
        if not message:
            self._set_response(200)
            return

        chat = message.get('chat', {})
        chat_id = str(chat.get('id'))
        if chat_id != TELEGRAM_CHAT_ID:
            logging.warning(f"Unauthorized chat id: {chat_id}")
            self._set_response(403)
            return

        photos = message.get('photo')
        if not photos:
            self._set_response(200)
            return

        # Create batch folder
        batch_stamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        batch_id = f'review_{batch_stamp}'
        batch_path = os.path.join(INBOX_DIR, batch_id)
        images_path = os.path.join(batch_path, 'images')
        os.makedirs(images_path, exist_ok=True)

        # Download each photo (highest resolution last in array)
        image_files = []
        for i, photo_info in enumerate(photos):
            file_id = photo_info.get('file_id')
            file_path = self.download_file(file_id, images_path)
            if file_path:
                image_files.append(os.path.basename(file_path))

        # Compose metadata
        caption = message.get('caption', '') or ''
        metadata = {
            'batch_id': batch_id,
            'source': 'telegram',
            'timestamp': datetime.utcnow().isoformat(),
            'caption': caption,
            'image_files': image_files
        }

        meta_path = os.path.join(batch_path, 'metadata.json')
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        logging.info(f"Batch {batch_id} created with {len(image_files)} images")

        self._set_response(200)
        self.wfile.write(json.dumps({'status': 'received'}).encode())

    def download_file(self, file_id, save_dir):
        file_url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}'
        try:
            r = requests.get(file_url)
            r.raise_for_status()
            file_info = r.json()
            file_path = file_info['result']['file_path']
            download_url = f'https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}'

            local_fname = os.path.basename(file_path)
            local_path = os.path.join(save_dir, local_fname)

            rdl = requests.get(download_url)
            rdl.raise_for_status()

            with open(local_path, 'wb') as f:
                f.write(rdl.content)

            return local_path
        except Exception as e:
            logging.error(f"Failed to download file: {e}")
            return None


def run(server_class=HTTPServer, handler_class=WebhookHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Starting Sixx Telegram webhook server on port {PORT}")
    print(f"Starting Sixx Telegram webhook server on port {PORT}")
    httpd.serve_forever()


if __name__ == '__main__':
    run()
