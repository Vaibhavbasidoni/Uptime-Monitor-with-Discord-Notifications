from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import threading
import time
from datetime import datetime
from app import models, schemas
from app.database import get_db, engine, SessionLocal
from app.monitor import check_website_status

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Uptime Monitor")

# Global flag to control the monitoring thread
monitor_active = True

def background_monitoring():
    while monitor_active:
        db = SessionLocal()
        try:
            websites = db.query(models.Website).all()
            current_time = datetime.utcnow()
            
            for website in websites:
                # Get the last check for this website
                last_check = db.query(models.StatusCheck)\
                    .filter(models.StatusCheck.website_id == website.id)\
                    .order_by(models.StatusCheck.checked_at.desc())\
                    .first()
                
                # Check if it's time to monitor this website
                if not last_check or (current_time - last_check.checked_at).total_seconds() >= website.check_interval_seconds:
                    check_website_status(db, website)
            
        except Exception as e:
            print(f"Error in monitoring thread: {e}")
        finally:
            db.close()
        
        # Sleep for a short interval before the next check
        time.sleep(10)  # Check every 10 seconds

# Start the background monitoring thread when the application starts
@app.on_event("startup")
def start_monitoring():
    thread = threading.Thread(target=background_monitoring, daemon=True)
    thread.start()

# Stop the monitoring thread when the application shuts down
@app.on_event("shutdown")
def stop_monitoring():
    global monitor_active
    monitor_active = False

@app.post("/sites", response_model=schemas.Website)
def add_site(site: schemas.WebsiteCreate, db: Session = Depends(get_db)):
    db_site = models.Website(
        url=str(site.url),
        name=site.name,
        check_interval_seconds=site.check_interval_seconds,
        expected_status_code=site.expected_status_code
    )
    db.add(db_site)
    try:
        db.commit()
        db.refresh(db_site)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="URL already exists")
    return db_site

@app.get("/sites", response_model=List[schemas.Website])
def list_sites(db: Session = Depends(get_db)):
    return db.query(models.Website).all()

@app.delete("/sites/{site_id}")
def delete_site(site_id: int, db: Session = Depends(get_db)):
    site = db.query(models.Website).filter(models.Website.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    db.delete(site)
    db.commit()
    return {"message": "Site deleted successfully"}

@app.get("/sites/{site_id}/history", response_model=List[schemas.StatusCheck])
def get_site_history(site_id: int, db: Session = Depends(get_db)):
    site = db.query(models.Website).filter(models.Website.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return db.query(models.StatusCheck).filter(models.StatusCheck.website_id == site_id).all()

@app.post("/webhook", response_model=schemas.DiscordWebhook)
def add_webhook(webhook: schemas.DiscordWebhookCreate, db: Session = Depends(get_db)):
    db_webhook = models.DiscordWebhook(url=str(webhook.url), name=webhook.name)
    db.add(db_webhook)
    try:
        db.commit()
        db.refresh(db_webhook)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Webhook URL already exists")
    return db_webhook 