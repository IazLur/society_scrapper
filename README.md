# society_scrapper

This project contains a small proof of concept for retrieving company information using the public `recherche-entreprises` API.

The original `search.py` script can still be used from the command line, but a small web application is now provided.

## Backend API

The Flask application in `app.py` exposes the features of `search.py` through a REST API and also implements a very small authentication system with SQLite.

### Install dependencies

```bash
pip install flask flask-cors werkzeug itsdangerous requests beautifulsoup4
```

### Run the API

```bash
python app.py
```

The API will create a local `app.db` SQLite database. Endpoints:

- `POST /api/register` with JSON `{username, email, password}`
- `POST /api/login` with JSON `{email, password}` returns a token
- `GET /api/search?domain=example.com` authenticated with header `Authorization: Bearer <token>`

## Frontend

A simple React application (Vite + Bootstrap) is located in the `frontend` folder.

### Install dependencies

```bash
cd frontend
npm install
```

### Start development server

```bash
npm run dev
```

The app provides a login/registration screen and, once logged in, a small interface to search for companies by domain.
