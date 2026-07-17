from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.crud import create_short_url, get_access_logs, get_original_url, get_recent_url_mappings, get_url_mapping, record_access
from app.database import get_db
from app.schemas import AccessLogResponse, URLResponse, URLStats, URLCreate

router = APIRouter(prefix="")


@router.post("/shorten", response_model=URLResponse, status_code=201)
def shorten_url(url_data: URLCreate, db: Session = Depends(get_db)):
    db_url, created = create_short_url(db, url_data.original_url, url_data.custom_alias)
    if not created:
        return JSONResponse(
            status_code=200,
            content=_format_response(db_url).model_dump(mode="json"),
        )
    return _format_response(db_url)


@router.get("/{code}")
def redirect_to_url(code: str, request: Request, db: Session = Depends(get_db)):
    db_url = get_original_url(db, code)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    record_access(
        db,
        short_code=code,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return RedirectResponse(url=db_url.original_url, status_code=301)


@router.get("/{code}/stats", response_model=URLStats)
def get_url_stats(code: str, db: Session = Depends(get_db)):
    db_url = get_url_mapping(db, code)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    logs = get_access_logs(db, code)
    return URLStats(
        url=_format_response(db_url),
        total_accesses=db_url.access_count,
        recent_accesses=[AccessLogResponse.model_validate(log) for log in logs],
    )


@router.get("/recent/urls", response_model=list[URLResponse])
def recent_links(limit: int = 10, db: Session = Depends(get_db)):
    urls = get_recent_url_mappings(db, limit)
    return [_format_response(u) for u in urls]


def _format_response(db_url) -> URLResponse:
    return URLResponse(
        id=db_url.id,
        short_code=db_url.short_code,
        short_url=f"{settings.base_url}/{db_url.short_code}",
        original_url=db_url.original_url,
        created_at=db_url.created_at,
        access_count=db_url.access_count,
        is_custom=bool(db_url.is_custom),
    )
