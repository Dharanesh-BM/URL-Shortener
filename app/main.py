from datetime import timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request, status, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
import jwt
from jose import JWTError

from app.config import get_settings
from app.models.database import get_db, engine, Base
from app.models.models import User, URL
from app.schemas.schemas import UserCreate, User as UserSchema, URLCreate, URL as URLSchema
from app.services.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user,
)
from app.services.url import (
    create_url,
    get_url_by_code,
    record_visit,
    get_url_stats,
    get_urls_by_user,
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=get_settings().PROJECT_NAME)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    access_token: str = Cookie(None)
):
    if not access_token:
        return RedirectResponse(url="/login")
    
    try:
        token = access_token.split(" ")[1] if " " in access_token else access_token
        payload = jwt.decode(token, get_settings().SECRET_KEY, algorithms=[get_settings().ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return RedirectResponse(url="/login")
    except JWTError:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request
    })


@app.post("/api/users/", response_model=UserSchema)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Also check username
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@app.post("/api/urls/", response_model=URLSchema)
async def create_short_url(
    url: URLCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return create_url(db=db, url=url, user_id=current_user.id)


@app.get("/api/urls/", response_model=List[URLSchema])
async def list_urls(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return get_urls_by_user(db=db, user_id=current_user.id)


@app.get("/api/urls/{url_id}/stats")
async def get_url_statistics(
    url_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    url = db.query(URL).filter(URL.id == url_id, URL.owner_id == current_user.id).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return get_url_stats(db=db, url_id=url_id)


@app.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    url = get_url_by_code(db=db, short_code=short_code)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Record the visit
    record_visit(
        db=db,
        url=url,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        referrer=request.headers.get("referer")
    )
    
    return RedirectResponse(url.original_url)


@app.delete("/api/urls/{url_id}")
async def delete_url(
    url_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    url = db.query(URL).filter(URL.id == url_id, URL.owner_id == current_user.id).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    db.delete(url)
    db.commit()
    return {"message": "URL deleted successfully"} 