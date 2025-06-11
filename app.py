import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import itsdangerous

import search

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-me'
CORS(app)

serializer = itsdangerous.URLSafeTimedSerializer(app.config['SECRET_KEY'])

def get_db():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, email TEXT UNIQUE, password TEXT)"
    )
    conn.commit()
    conn.close()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'invalid data'}), 400
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (username, email, password) VALUES (?,?,?)',
            (data['username'], data['email'], generate_password_hash(data['password']))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'user exists'}), 400
    return jsonify({'status': 'ok'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    cur = conn.execute('SELECT * FROM users WHERE email=?', (data.get('email'),))
    row = cur.fetchone()
    if not row or not check_password_hash(row['password'], data.get('password','')):
        return jsonify({'error': 'invalid credentials'}), 401
    token = serializer.dumps({'user_id': row['id']})
    return jsonify({'token': token, 'username': row['username']})

def require_auth(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization','')
        if not auth.startswith('Bearer '):
            return jsonify({'error':'missing token'}), 401
        token = auth.split(' ')[1]
        try:
            data = serializer.loads(token, max_age=3600*24)
        except itsdangerous.BadSignature:
            return jsonify({'error':'invalid token'}), 401
        request.user_id = data['user_id']
        return f(*args, **kwargs)
    return wrapper

@app.route('/api/search')
@require_auth
def search_companies():
    query = request.args.get('q') or request.args.get('domain')
    if not query:
        return jsonify({'error':'missing query'}), 400
    if '.' in query:
        params = {'name': search.guess_company_name(query)}
    else:
        params = search.parse_natural_query(query)
    companies = search.search_company(
        params['name'],
        ape=request.args.get('ape'),
        departement=params.get('departement') or request.args.get('departement'),
        region=params.get('region') or request.args.get('region'),
        ville=params.get('ville') or request.args.get('ville'),
    )
    for c in companies:
        c['score'] = search.compute_score(c)
    companies.sort(key=lambda x: x['score'], reverse=True)
    return jsonify({'name': params['name'], 'results': companies})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
