# enviar a telegram los libros que aparecen como sin enviar en la base de datos
# marcarlos como enviados, y agregar el magnet link para descargarlos

import sqlite3
import requests
from bs4 import BeautifulSoup
import telegram
import time
from itertools import chain
from telegraph import Telegraph
import os
from dotenv import load_dotenv


def get_new_books():
    "retorna una lista: links de los libros que no fueron enviados"
    
    con = sqlite3.connect(os.environ.get('path_db'))
    cur = con.cursor()
    try:
        res = cur.execute("SELECT link FROM books WHERE sent=''")
        res = [link[0] for link in res.fetchall()]
        return res
    except:
        logs = open(os.environ.get('path_logs'), 'a')
        logs.write('[Error] La base de datos no existe.\n')
        return []
    
    
def get_books_info(new_books):
    """toma una lista de links y devuelve otra lista con informacion de cada libro
    dentro de un diccionario"""
    
    books = []
    
    for link in new_books:
        try:
            r = requests.get('https://' + link)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # genres
            genres = []
            table = soup.find('td', width="58%")
            elements = table.find_all('tr')
            for n in range(len(elements)):
                genres.append(elements[n].find_all('td')[1].text.strip())
            divided_genres = list(chain(*[i.split(', ') for i in genres]))
            
            mapping = {
                'No Ficción': 'NoFicción',
                'Publicaciones periódicas': 'PublicacionesPeriódicas',
                'Ciencias exactas': 'CienciasExactas',
                'Ciencias naturales': 'CienciasNaturales',
                'Ciencias sociales': 'CienciasSociales',
                'Crítica y teoría literaria': 'CríticaYTeoríaLiteraria',
                'Diccionarios y enciclopedias': 'DiccionariosYEnciclopedias',
                'Manuales y cursos': 'ManualesYCursos',
                'Obras completas': 'ObrasCompletas',
                'Salud y bienestar': 'SaludYBienestar',
                'Ciencia ficción': 'CienciaFicción'}
            
            remove_spaces = [mapping[word] if word in mapping else word for word in divided_genres]
            genres_list = ["#" + word for word in remove_spaces]
            
            # telegraph
            telegraph = Telegraph()
            telegraph.create_account(short_name='epublibre-editor')

            telegraph_link = telegraph.create_page(
                title = soup.find('div', class_='titulo').text.strip(),
                html_content = (
                    '<h3>Sinopsis</h3>'
                    f'<p>{str(soup.find("div", class_="ali_justi").span)[6:-7]}</p>'))
            
            # rest of the book information
            books.append(
                {'title':soup.find('div', class_='titulo').text.strip(),
                'author':soup.find('div', class_='negrita aut_sec').a.text.strip(),
                'pages':soup.find('span', class_='well_blue btn-small negrita celda-info').text.strip(),
                'date':soup.find_all('span', class_='well_blue btn-small negrita')[1].text.strip(),
                'magnet_link':soup.find('a', id='en_desc').get('href'),
                'cover':soup.find('img', id='portada')['src']+"&random=234",
                'genres':genres_list,
                'telegraph_link':telegraph_link['url'],
                'book_link':link})
            time.sleep(5)
                  
        except Exception as e:
            logs = open(os.environ.get('path_logs'), 'a')
            logs.write(f'[Error] Al scrapear el libro {e}.\n')

    return books


def send_to_tg(new_books):
    """toma una lista de libros y los envia a telegram. devuelve una lista con
    los links de los libros que logro enviar"""
    
    books_sent = []
    
    for book in new_books:
        mensaje = (       
            f"📘 | {book['title']}\n\n"
            f"👤 | {book['author']}\n"
            f"📆 | {book['date']}\n"
            f"📄 | {book['pages']}\n"
            f"📁 | {' '.join(book['genres'])}\n\n"
            f"{book['telegraph_link']}")

        try:
            bot.send_photo(chat_id=os.environ.get('chat_id'), photo=book['cover'], caption=mensaje)
            books_sent.append({'book_link':book['book_link'], 'magnet_link':book['magnet_link']})
        except:
            try:
                bot.send_photo(chat_id=os.environ.get('chat_id'), photo='https://i.imgur.com/tM7n9i3.png', caption=mensaje)
                books_sent.append({'book_link':book['book_link'], 'magnet_link':book['magnet_link']})

            except Exception as e:
                logs = open(os.environ.get('path_logs'), 'a')
                logs.write(f'[Error] No se pudo enviar el libro {e}.\n')
        
        time.sleep(5)


    return books_sent


def update_database(books_sent):
    """toma una lista de links y la usa para actualizar los libros que lograron
    enviarse a telegram"""
    
    for book in books_sent:
        con = sqlite3.connect(os.environ.get('path_db'))
        cur = con.cursor()
        
        cur.execute(f"""UPDATE books SET sent='True', magnet_link='{book['magnet_link']}'
                    WHERE link='{book['book_link']}'""")
        con.commit()

    
load_dotenv()
new_books = get_new_books()
bot = telegram.Bot(os.environ.get('token_bot'))
books_info = get_books_info(new_books)
books_sent = send_to_tg(books_info)
update_database(books_sent)   



    
    