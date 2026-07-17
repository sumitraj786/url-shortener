from sqlalchemy.orm import Session

from app.models import AccessLog, Counter, URLMapping
from app.utils import encode_base62


def generate_short_code(db: Session) -> str:
    counter = db.query(Counter).with_for_update().first()
    counter.value += 1
    db.flush()
    return encode_base62(counter.value)


def create_short_url(db: Session, original_url: str, custom_alias: str | None = None) -> tuple[URLMapping, bool]:
    existing = db.query(URLMapping).filter(URLMapping.original_url == original_url).first()
    if existing:
        return existing, False

    if custom_alias:
        alias_taken = db.query(URLMapping).filter(URLMapping.short_code == custom_alias).first()
        if alias_taken:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=409,
                detail={"detail": "Custom alias already taken", "error_code": "ALIAS_TAKEN"},
            )
        short_code = custom_alias
        is_custom = 1
    else:
        short_code = generate_short_code(db)
        is_custom = 0

    db_url = URLMapping(
        original_url=original_url,
        short_code=short_code,
        is_custom=is_custom,
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url, True


def get_url_mapping(db: Session, short_code: str) -> URLMapping | None:
    return db.query(URLMapping).filter(URLMapping.short_code == short_code).first()


def get_original_url(db: Session, short_code: str) -> URLMapping | None:
    db_url = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
    if db_url:
        db_url.access_count += 1
        db.commit()
    return db_url


def record_access(db: Session, short_code: str, ip_address: str | None, user_agent: str | None) -> AccessLog:
    log = AccessLog(
        short_code=short_code,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_access_logs(db: Session, short_code: str, limit: int = 50) -> list[AccessLog]:
    return (
        db.query(AccessLog)
        .filter(AccessLog.short_code == short_code)
        .order_by(AccessLog.accessed_at.desc())
        .limit(limit)
        .all()
    )


def search_url_mappings(db: Session, query: str) -> list[URLMapping]:
    return db.query(URLMapping).filter(URLMapping.original_url.contains(query)).all()


def get_recent_url_mappings(db: Session, limit: int = 10) -> list[URLMapping]:
    return db.query(URLMapping).order_by(URLMapping.created_at.desc()).limit(limit).all()


def delete_url_mapping(db: Session, short_code: str) -> bool:
    obj = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
