# Shortr

A URL shortener built with FastAPI and PostgreSQL — paste a long link, get a short one back, with QR codes and click tracking built in.

**Live demo:** https://urlshortener-i0ur.onrender.com

## Features

- Shorten any URL into a short, shareable code
- Automatic redirect from short link to original URL
- QR code generated for every short link
- Click count tracking per link
- Paste-from-clipboard button and Enter-to-submit for faster input
- Clean, minimal web UI — no page reloads, just fetch calls to the API

## Tech stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL, accessed via SQLAlchemy
- **Local dev:** Dockerized Postgres
- **Production database:** Neon (serverless Postgres)
- **Deployment:** Docker container on Render
- **Frontend:** Plain HTML/CSS/JS, no framework

## API endpoints

| Method | Path                  | Description                              |
|--------|-----------------------|-------------------------------------------|
| GET    | `/`                    | Serves the web UI                        |
| POST   | `/shorten`             | Takes a URL, returns a short code + link |
| GET    | `/{short_code}`        | Redirects to the original URL, increments click count |
| GET    | `/qr/{short_code}`     | Returns a QR code image for the link     |
| GET    | `/stats/{short_code}`  | Returns the original URL and click count |

## Running it locally

**1. Clone the repo and set up a virtual environment:**
```bash
git clone https://github.com/YOUR_USERNAME/url-shortener.git
cd url-shortener
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Start a local Postgres instance with Docker:**
```bash
docker run -d \
  --name url-shortener-db \
  -e POSTGRES_USER=urlshortener \
  -e POSTGRES_PASSWORD=devpassword \
  -e POSTGRES_DB=urlshortener \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16
```

**3. Create a `.env` file** in the project root:

DATABASE_URL=postgresql://urlshortener:devpassword@localhost:5432/urlshortener


**4. Run the app:**
```bash
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000` in your browser.

## Deployment

The app runs in a Docker container on Render, with `DATABASE_URL` pointing to a Neon-hosted Postgres instance in production instead of the local Docker one. Any schema changes to the SQLAlchemy models require manually rebuilding the table (`DROP TABLE url_mappings;`) on both the local and Neon databases, since `create_all()` only creates missing tables — it doesn't alter existing ones.