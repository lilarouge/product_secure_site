from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import ssl
import sqlite3
from pysqlcipher3 import dbapi2 as sqlite
import os
import html
import json
import re
import time
from collections import defaultdict



HOST = "localhost"
PORT = 8443

#Create the data base SQLite and encrypts it through SQLCipher storing the secret code in an environment variable

DB_FILE = "products.db"
DB_KEY = os.environ.get("DB_KEY")

# Rate limiting max 5 requests per 60 seconds per IP
RATE_LIMIT = 5
RATE_WINDOW = 60  
request_counts = defaultdict(list)

def is_rate_limited(ip):
    now = time.time()
    # Keep only requests within the time window
    request_counts[ip] = [t for t in request_counts[ip] if now - t < RATE_WINDOW]
    if len(request_counts[ip]) >= RATE_LIMIT:
        return True
    request_counts[ip].append(now)
    return False

def init_db():
    conn = sqlite.connect(DB_FILE)
    conn.execute(f"PRAGMA key='{DB_KEY}';")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        price REAL NOT NULL
    )
    """)

    conn.commit()
    conn.close()

#Setting the HTTP requests

class MyServer(BaseHTTPRequestHandler):

    # Serve GET requests (encodes from string to bytes to send from the server to the browser) and sets Content Security Policy to prevent XSS attacks 
    def do_GET(self):
        if self.path == "/":
            with open("index.html", "r") as file:
                html = file.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'")
            self.end_headers()
            self.wfile.write(html.encode())

        elif self.path == "/style.css":
            with open("style.css", "r") as file:
                css = file.read()
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            self.wfile.write(css.encode())

        elif self.path == "/script.js":
            with open("script.js", "r") as file:
                js = file.read()
            self.send_response(200)
            self.send_header("Content-type", "application/javascript")
            self.end_headers()
            self.wfile.write(js.encode())
        
        elif self.path == "/search.html":
            with open("search.html", "r") as file:
                html_content = file.read()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'")
            self.end_headers()
            self.wfile.write(html_content.encode())

        elif self.path == "/search.js":
            with open("search.js", "r") as file:
                js_content = file.read()
            self.send_response(200)
            self.send_header("Content-type", "application/javascript")
            self.end_headers()
            self.wfile.write(js_content.encode())
            
        elif self.path.startswith("/search"):
            # Parse the query string
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("query", [""])[0]


            # Server-side validation: letters and spaces only
            if not re.fullmatch(r"[A-Za-z\s]+", query):
                # Invalid input: return empty results or 400 error
                self.send_response(400)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Invalid input: only letters and spaces are allowed")
                return    


            # Connect to the encrypted database
            conn = sqlite.connect(DB_FILE)
            conn.execute(f"PRAGMA key='{DB_KEY}';")
            cursor = conn.cursor()


            # Searching for the query with parameterized query to avoid SQL injections 
            cursor.execute("SELECT name, price FROM products WHERE name LIKE ?",('%' + query + '%',))
            results = cursor.fetchall()
            conn.close()

            # Return JSON response
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps([{"name": r[0], "price": r[1]} for r in results]).encode())

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

    # Handle POST requests with html.escape to prevent XSS attacks on input fields
    def do_POST(self):
        if self.path == "/add-product":
            ip = self.client_address[0]
            if is_rate_limited(ip):
                self.send_response(429)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Too many requests. Please wait.")
                return
            
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode()
            data = urllib.parse.parse_qs(body)
            

            # Extract form fields
            name = data.get("name", [""])[0]
            price = data.get("price", [""])[0]

            # Validate price is not negative
            try:
                price_value = float(price)
                if price_value < 0:
                    raise ValueError()
            except:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid price")
                return

            # Validate name is only letters
            if not re.fullmatch(r"[A-Za-z\s]+", name):
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid product name: only letters and spaces allowed")
                return

            # Escape name to prevent XSS attacks
            safe_name = html.escape(name)

            conn = sqlite.connect(DB_FILE)
            conn.execute(f"PRAGMA key='{DB_KEY}';")
            cursor = conn.cursor()  

            # Check if the product already exists
            cursor.execute("SELECT id FROM products WHERE LOWER(name) = LOWER(?)", (name,))
            existing = cursor.fetchone()
            if existing:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Product already exists") 
                conn.close()
                return

            # Insert into DB if all good 
            cursor.execute(
                "INSERT INTO products (name, price) VALUES (?, ?)",
                (safe_name, price_value)
            )



            conn.commit()
            conn.close()

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Product added successfully!")

# Start the server with HTTPS (TLS encrypting the transport)
if __name__ == "__main__":
    init_db()

    httpd = HTTPServer((HOST, PORT), MyServer)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="localhost.pem", keyfile="localhost-key.pem")

    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"Secure server running at https://{HOST}:{PORT}")
    httpd.serve_forever()
