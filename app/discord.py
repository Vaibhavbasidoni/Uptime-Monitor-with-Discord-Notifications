import requests
from datetime import datetime, UTC
from app import models
from typing import Optional

def send_discord_notification(
    webhook_url: str,
    website: models.Website,
    status_check: models.StatusCheck,
    previous_status: Optional[str]
) -> None:
    if status_check.status == "down":
        title = "🔴 Website Down Alert"
        color = 0xFF0000  # Red
    else:
        title = "🟢 Website Recovery Alert"
        color = 0x00FF00  # Green

    site_name = website.name or website.url
    
    embed = {
        "title": title,
        "color": color,
        "fields": [
            {
                "name": "Site",
                "value": f"{site_name} ({website.url})",
                "inline": False
            },
            {
                "name": "Status",
                "value": status_check.status.upper(),
                "inline": True
            },
            {
                "name": "Time",
                "value": status_check.checked_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "inline": True
            }
        ],
        "timestamp": datetime.now(UTC).isoformat()
    }

    if status_check.error_message:
        embed["fields"].append({
            "name": "Error",
            "value": status_check.error_message,
            "inline": False
        })

    if status_check.response_time_ms:
        embed["fields"].append({
            "name": "Response Time",
            "value": f"{status_check.response_time_ms:.2f}ms",
            "inline": True
        })

    payload = {
        "embeds": [embed]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        # Log the error but don't raise it to prevent monitoring disruption
        print(f"Failed to send Discord notification: {e}") 