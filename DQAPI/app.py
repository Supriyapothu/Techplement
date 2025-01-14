'''
Created on Jun 29, 2024

@author: Admin


'''

import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            author TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '_main_':
    init_db()




import json
import random


from http.server import BaseHTTPRequestHandler, HTTPServer

DB_PATH = 'database.db'

class RequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()



    def do_GET(self):
        
        if self.path == '/quote':
            self.get_quote()
        elif self.path.startswith('/quotes/search'):
            self.search_quotes()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def do_POST(self):
        
        if self.path == '/quote':
            self.add_quote()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def do_PUT(self):
        if self.path.startswith('/quote/'):
            self.update_quote()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def do_DELETE(self):
        if self.path.startswith('/quote/'):
            self.delete_quote()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def get_quote(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM quotes')
        quotes = c.fetchall()
        conn.close()
        if not quotes:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "No quotes available"}).encode())
        else:
            quote = random.choice(quotes)
            self._set_headers()
            self.wfile.write(json.dumps({"text": quote[1], "author": quote[2]}).encode())

    def add_quote(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        text = data['text']
        author = data['author']

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO quotes (text, author) VALUES (?, ?)', (text, author))
        conn.commit()
        conn.close()
        
        self._set_headers(201)
        self.wfile.write(json.dumps({"message": "Quote added successfully"}).encode())

    def update_quote(self):
        quote_id = int(self.path.split('/')[-1])
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        text = data.get('text')
        author = data.get('author')

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM quotes WHERE id = ?', (quote_id,))
        quote = c.fetchone()
        if quote:
            c.execute('UPDATE quotes SET text = ?, author = ? WHERE id = ?', (text, author, quote_id))
            conn.commit()
            self._set_headers()
            self.wfile.write(json.dumps({"message": "Quote updated successfully"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Quote not found"}).encode())
        conn.close()

    def delete_quote(self):
        quote_id = int(self.path.split('/')[-1])

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM quotes WHERE id = ?', (quote_id,))
        quote = c.fetchone()
        if quote:
            c.execute('DELETE FROM quotes WHERE id = ?', (quote_id,))
            conn.commit()
            self._set_headers()
            self.wfile.write(json.dumps({"message": "Quote deleted successfully"}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Quote not found"}).encode())
        conn.close()

    def search_quotes(self):
        author = self.path.split('=')[-1]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM quotes WHERE author LIKE ?', ('%' + author + '%',))
        quotes = c.fetchall()
        conn.close()

        if quotes:
            self._set_headers()
            self.wfile.write(json.dumps([{"text": q[1], "author": q[2]} for q in quotes]).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "No quotes found for the given author"}).encode())

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '_main_':
    run()
