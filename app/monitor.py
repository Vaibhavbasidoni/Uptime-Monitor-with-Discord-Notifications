import requests
import time
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from app import models
from app.discord import send_discord_notification
from typing import Optional

def check_website_status(db: Session, website: models.Website) -> models.StatusCheck:
    start_time = time.time()
    status = "up"
    error_message = None
    response_time = None
    last_status_change = None
    
    try:
        response = requests.get(
            str(website.url), 
            timeout=10,
            allow_redirects=True
        )
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code != website.expected_status_code:
            status = "down"
            error_message = f"Unexpected status code: {response.status_code}"
            
    except requests.RequestException as e:
        status = "down"
        error_message = str(e)
    
    # Get previous status check
    previous_check = db.query(models.StatusCheck)\
        .filter(models.StatusCheck.website_id == website.id)\
        .order_by(models.StatusCheck.checked_at.desc())\
        .first()
    
    # Set last_status_change if status changed
    if not previous_check or previous_check.status != status:
        last_status_change = datetime.now(UTC)
    
    # Create status check record
    status_check = models.StatusCheck(
        website_id=website.id,
        status=status,
        response_time_ms=response_time,
        error_message=error_message,
        checked_at=datetime.now(UTC),
        last_status_change=last_status_change
    )
    
    db.add(status_check)
    
    # Send Discord notification if status changed
    if not previous_check or previous_check.status != status:
        webhooks = db.query(models.DiscordWebhook).all()
        for webhook in webhooks:
            send_discord_notification(
                webhook_url=webhook.url,
                website=website,
                status_check=status_check,
                previous_status=previous_check.status if previous_check else None
            )
    
    db.commit()
    return status_check 