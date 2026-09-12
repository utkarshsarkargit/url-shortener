from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import string
import random

from database import SessionLocal, URLMapping

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class URLRequest(BaseModel):
    url: str

def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.get("/")
def read_root():
    return FileResponse("static/index.html")


@app.post("/shorten")
def shorten_url(body: URLRequest, request: Request, db: Session = Depends(get_db)):
    original = body.url
    if not original.startswith(("http://", "https://")):
        original = "https://" + original
    
    short_code = generate_short_code()
    db.add(URLMapping(short_code=short_code, original_url=original))
    db.commit()
    return {"short_code": short_code, "short_url": f"{request.base_url}{short_code}"}

@app.get("/{short_code}")
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    entry = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=entry.original_url)
