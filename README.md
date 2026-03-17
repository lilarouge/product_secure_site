# Product Manager - Secure Web Application

A secure two-page web application for managing products, built with Python 
and SQLite.

## Features

- Add products (name + price) via a web form
- Search products by name
- Protected against **SQL Injection** using parameterized queries
- Protected against **XSS attacks** using input validation, HTML escaping, 
and Content Security Policy headers
- **Rate limiting** on all endpoints (max 5 requests per 60 seconds per 
IP)
- **Encrypted database** at rest using SQLCipher
- **HTTPS/TLS** transport encryption

## Requirements

- Python 3.x
- pysqlcipher3

Install dependencies:
```bash
pip install pysqlcipher3
```

## Setup & Running

### 1. Set the database encryption key
```bash
export DB_KEY=your_secret_key_here
```

### 2. Generate SSL certificates (if you don't have them)
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 
-nodes
```

### 3. Run the server
```bash
python server.py
```

### 4. Open in browser
```
https://localhost:8443
```
> Note: Accept the security warning for self-signed certificates, or use 
`mkcert` for a locally trusted cert.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DB_KEY` | Encryption key for the SQLCipher database |

## Security Measures

| Threat | Protection |
|--------|------------|
| SQL Injection | Parameterized queries everywhere |
| XSS | Input validation (regex), html.escape(), CSP headers |
| Brute Force | Rate limiting (5 req/60s per IP) |
| Data at Rest | SQLCipher encrypted database |
| Transport | HTTPS/TLS with SSL certificate |
