# Este bot recorre un directorio buscando archivos epub y los envia a tg

import telegram
import os
import time
from dotenv import load_dotenv

load_dotenv()
books_path = os.environ.get('path_books')
bot = telegram.Bot(os.environ.get('token_bot'))

for book in os.listdir(books_path):
    if book.endswith('.epub'):
        try:
            file_path = os.path.join(books_path, book)
            bot.send_document(chat_id=os.environ.get('chat_id_files'),
                            document=open(file_path, 'rb'),
                            caption=f'`{book}`', parse_mode='MarkdownV2')
            os.unlink(file_path)
            time.sleep(5)
        except Exception as e:
            logs = open(os.environ.get('path_logs'), 'a')
            logs.write(f'[Error] al enviar el archivo a telegram {e}.\n')
