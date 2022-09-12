# traer los magnet link de la base de datos, agregarlos a qbt y marcar en la 
# base de datos que ya se estan descargando.

import sqlite3
import subprocess
import time
import os
from dotenv import load_dotenv

def get_magnet_links():
    "retorna una lista: magnet links de los libros que no fueron descargados"
    
    con = sqlite3.connect(os.environ.get('path_db'))
    cur = con.cursor()
    try:
        res = cur.execute("""SELECT magnet_link FROM books WHERE downloaded=''
                          AND magnet_link <> ''""")
        res = [link[0] for link in res.fetchall()]
        return res
    except:
        logs = open(os.environ.get('path_logs'), 'a')
        logs.write('[Error] La base de datos no existe.\n')
        return []


def update_downloaded_books(books_downloaded):
    for book in books_downloaded:
        con = sqlite3.connect(os.environ.get('path_db'))
        cur = con.cursor()
        
        try:
            cur.execute(f"""UPDATE books SET downloaded='True' WHERE magnet_link='{book}'""")
            con.commit()
        except Exception as e:
            logs = open(os.environ.get('path_logs'), 'a')
            logs.write(f'[Error] Al actualizar la base de datos downloaded, {e}.\n')

load_dotenv()
magnet_links = get_magnet_links()

for magnet in magnet_links:
    try:
        subprocess.run(["transmission-remote", "-a", magnet])
        time.sleep(1)
    except Exception as e:
        logs = open(os.environ.get('path_logs'), 'a')
        logs.write(f'[Error] No se pudo descargar el archivo, {e}.\n')
        