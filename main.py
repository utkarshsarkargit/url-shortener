from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import string
import random
import qrcode
import io

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
    entry.click_count += 1
    db.commit()
    return RedirectResponse(url=entry.original_url)

@app.get("/qr/{short_code}")
def get_qr_code(short_code: str, request: Request, db: Session = Depends(get_db)):
    entry = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    short_url = f"{request.base_url}{short_code}"
    img = qrcode.make(short_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

@app.get("/stats/{short_code}")
def get_stats(short_code: str, db: Session = Depends(get_db)):
    entry = db.query(URLMapping).filter(URLMapping.short_code == short_code).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return {"original_url": entry.original_url, "click_count": entry.click_count}