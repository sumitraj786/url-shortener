import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, SessionLocal, engine
from app.models import Counter
from app.routers import urls


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(Counter).first():
        db.add(Counter(value=1))
        db.commit()
    db.close()
    yield


app = FastAPI(
    title="URL Shortener",
    description="A feature-rich URL shortener with analytics, QR codes, and custom aliases.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    response.headers["X-Process-Time-Ms"] = str(round(elapsed * 1000, 2))
    return response


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "url-shortener", "version": "1.0.0"}


app.include_router(urls.router, tags=["URLs"])

app.mount("/", StaticFiles(directory="static", html=True), name="static")
