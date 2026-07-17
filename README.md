# URL Shortener

A simple URL shortener that actually works. Paste a long link, get a short one. See how many people clicked it. Done.

What it does

- Turns long URLs into short ones (like https://short.link/abc123)
- Lets you pick your own short name if you want (like https://short.link/my-link)
- If you shorten the same URL twice, it gives you back the same short code - no duplicates
- Counts every click and logs the IP and browser info
- Gives you a simple web page to use it, plus API endpoints if you want to automate things

What's inside

| Piece | What I used

Web framework | FastAPI

Database | SQLAlchemy + SQLite

Validation | Pydantic

Testing | pytest

Frontend | Plain HTML + CSS + JavaScript (no frameworks)

How to set it up

You'll need Python 3.11 or newer.

# 1. Get the code

git clone https://github.com/sumitraj786/url-shortener.git

cd url-shortener

# 2. Make a virtual environment (keeps things clean)

python -m venv venv

venv\Scripts\activate # Windows

source venv/bin/activate # Mac / Linux

# 3. Install what you need

pip install -r requirements.txt

How to run it

python -m uvicorn app.main:app --reload

Open http://localhost:8000 in your browser. You'll see a page where you can paste a URL and shorten it right away.

If you prefer clicking around an API explorer, go to http://localhost:8000/docs instead - Swagger will show you every endpoint with a "Try it out" button.

Settings you can change

Create a .env file in the project folder to override these:

| Setting | What it does | Default value |
| DATABASEURL | Where to store data | sqlite:///./urlshortener.db |
| BASE_URL | The domain for generated short links | http://localhost:8000 |
| SHORTCODELENGTH | (not really used anymore) | 6 |

Example .env:

DATABASE_URL=sqlite:///./production.db

BASE_URL=https://myshortener.com

Using the web interface

The app comes with a built-in web page at http://localhost:8000/.

To shorten a URL:

1. Type or paste your long URL

2. Optionally add a custom short name

3. Click "Shorten"

4. Copy the short link, open it, or check its analytics

To check stats:

- Click the "Analytics" tab, type a short code, and see how many times it was visited
- Click the "Recent" tab to see the last 10 URLs you shortened

Using the API

If you want to automate things, here are the three endpoints.

# Make a short URL

POST /shorten

curl -X POST http://localhost:8000/shorten \

-H "Content-Type: application/json" \

-d '{"original_url": "https://example.com/very/long/page"}'

You'll get back something like:

{

"short_code": "1",

"short_url": "http://localhost:8000/1",

"original_url": "https://example.com/very/long/page",

"access_count": 0,

"is_custom": false

}

If you shorten the same URL again, you get a 200 (not 201) with the same short code - no duplicates created.

You can also pick your own short name:

curl -X POST http://localhost:8000/shorten \

-H "Content-Type: application/json" \

-d '{"originalurl": "https://python.org", "customalias": "python"}'

Now http://localhost:8000/python redirects to Python's website. If someone else already took that name, you'll get a 409 error.

What can go wrong:

| Status | Meaning |

| 201 | New short URL created |
| 200 | That URL was already shortened, here's the same code |
| 409 | Someone already took that custom alias |
| 422 | Your URL doesn't start with http:// or https:// |

# Redirect someone

GET /{code}

curl -I http://localhost:8000/1

You'll get a 301 response with a Location header pointing to the original URL. Your browser will follow this automatically.

If the code doesn't exist, you'll get a 404.

# See click stats

GET /{code}/stats

curl http://localhost:800/1/stats

Returns something like:

{

"url": {

"short_code": "1",

"short_url": "http://localhost:8000/1",

"original_url": "https://example.com",

"access_count": 5

},

"total_accesses": 5,

"recent_accesses": [

{

"accessed_at": "2026-07-15T18:10:00",

"ip_address": "127.0.0.1",

"user_agent": "curl/8.4"

}

]

}

Running the tests

python -m pytest tests/ -v

Seven tests that check everything actually works:

| Test name | What it checks |
| testpostshortenvalidurlreturnsshort_code | Shortening a URL gives back a 201 and a code |
| testpostshortensameurltwicereturnssamecode | Same URL twice = same code (no duplicates) |
| testpostshortenwithcustom_alias | Custom aliases work and redirect correctly |
| testgetcoderedirectstooriginalurl | GET /{code} returns a 301 to the right place |
| testgetcodeunknowncodereturns404 | Unknown codes give a 404 |
| testurlvalidationrejectsinvalid_urls | Bad URLs (not-a-url, ftp://...) get rejected |
| testcustomaliasconflicthandling | Using an alias someone else took returns 409 |

Why I built it this way

Short codes are just numbers.  Instead of generating random strings and hoping they don't collide, I use a counter. The first URL gets code 1, the second gets 2, and so on. 

Then I convert that number to base62 (digits + lowercase + uppercase) so 1000 becomes something like g8. 

No collisions, ever.

301 redirects, not 307. A 301 tells your browser "remember this and don't ask again." So repeat visits skip the shortener entirely and go straight to the destination. Faster for everyone.

Duplicate URLs return the same code. If you shorten the same link twice, you get the same short code back. No duplicate entries, no confusion about which short link points where.

The frontend is just HTML. No React, no build step, no npm install. Open the page and it works. It calls the same API endpoints you'd use from curl.

SQLite for dev, swap later. SQLite doesn't need a server or Docker. When you need PostgreSQL in production, change one line in the config file.