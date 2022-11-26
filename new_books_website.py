import sqlite3
import re
import requests
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv
import os

def create_database():
    con = sqlite3.connect(os.environ.get('path_db'))
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS books
                (link TEXT,
                sent TEXT,
                downloaded TEXT,
                magnet_link TEXT)''')

def get_books_db():
    "Return a list with the links of the books in the database"
    con = sqlite3.connect(os.environ.get('path_db'))
    cur = con.cursor()
    try:
        res = cur.execute("SELECT link FROM books")
        res = [link[0] for link in res.fetchall()]
        return res
    except:
        logs = open(os.environ.get('path_logs'), 'a')
        logs.write('[Error] La base de datos no existe. Creando la base de datos.\n')
        create_database()
        return []

def get_books_website():
    "Return a list with the links of the books in the website"
    
    books_links = []
    num_pages = 2
    
    try:
        for page in range(num_pages):
            url = f'https://epublibre.org/catalogo/index/{page*18}/nuevo/novedades/sin/1'
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            books = soup.find_all('a', attrs={"id":"stk"})

            for book in books:
                link_pattern = r"epublibre.*"
                book_link = re.search(link_pattern, book['href']).group()
                books_links.append(book_link)

            time.sleep(5)
                
    except Exception as e:
        logs = open(os.environ.get('path_logs'), 'a')
        logs.write(f'[Error] Al intentar traer los libros de la pagina: {e}\n')
        
    return books_links

load_dotenv()
books_website = get_books_website()
books_db = get_books_db()
    
for book in books_website:
    if book not in books_db:
        con = sqlite3.connect(os.environ.get('path_db'))
        cur = con.cursor()
        cur.execute('INSERT INTO books VALUES (?, ?, ?, ?)', (book, '', '', ''))
        con.commit()




