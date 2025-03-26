from datetime import datetime
import secrets
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import URL, URLVisit
from app.schemas.schemas import URLCreate
from datetime import timezone
from app.config import get_settings


def create_random_code(length: int = 6) -> str:
    return secrets.token_urlsafe(length)[:length]


def create_url(db: Session, url: URLCreate, user_id: int) -> URL:
    short_code = url.custom_alias or create_random_code()
    
    # Check if custom alias is already taken
    if url.custom_alias:
        existing_url = db.query(URL).filter(URL.short_code == short_code).first()
        if existing_url:
            raise HTTPException(status_code=400, detail="Custom alias already taken")
    
    db_url = URL(
        original_url=str(url.original_url),
        short_code=short_code,
        custom_alias=url.custom_alias,
        expires_at=url.expires_at,
        owner_id=user_id
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    # Add the full shortened URL to the response
    settings = get_settings()
    # Create the full shortened URL by combining the base URL and short code
    db_url.short_url = f"{settings.BASE_URL}/{db_url.short_code}"
    
    return db_url


def get_url_by_code(db: Session, short_code: str) -> Optional[URL]:
    url = db.query(URL).filter(URL.short_code == short_code).first()
    if not url:
        return None
    
    if url.expires_at and url.expires_at < datetime.now(timezone.utc):
        url.is_active = False
        db.commit()
        return None
    
    return url


def get_urls_by_user(db: Session, user_id: int) -> List[URL]:
    return db.query(URL).filter(URL.owner_id == user_id).all()


def record_visit(db: Session, url: URL, ip_address: str, user_agent: str, referrer: Optional[str] = None) -> URLVisit:
    visit = URLVisit(
        url_id=url.id,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit


def get_url_stats(db: Session, url_id: int) -> dict:
    url = db.query(URL).filter(URL.id == url_id).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    visits = url.visits
    total_visits = len(visits)
    
    # Get unique visitors by IP
    unique_visitors = len(set(visit.ip_address for visit in visits))
    
    # Get referrer statistics
    referrer_stats = {}
    for visit in visits:
        if visit.referrer:
            referrer_stats[visit.referrer] = referrer_stats.get(visit.referrer, 0) + 1
    
    # Sort referrers by visit count
    top_referrers = sorted(referrer_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_visits": total_visits,
        "unique_visitors": unique_visitors,
        "top_referrers": [ref[0] for ref in top_referrers]
    } 