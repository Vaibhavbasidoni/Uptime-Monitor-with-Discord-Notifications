# Website Uptime Monitor with Discord Notifications

A Python-based service that monitors website availability and sends notifications through Discord webhooks when a site goes down or recovers.

## Features

- Monitor multiple websites with configurable check intervals
- Track uptime/downtime history with response times
- Discord notifications for status changes
- RESTful API for managing monitored sites
- Real-time status monitoring
- Detailed error tracking

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite 
- **Background Tasks**: Threading
- **Notifications**: Discord Webhooks

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd uptime-monitor
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```env
DATABASE_URL=sqlite:///./uptime_monitor.db
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

### Endpoints

#### 1. Add Website to Monitor
```http
POST /sites
```
Request body:
```json
{
    "url": "https://example.com",
    "name": "Example Site",
    "check_interval_seconds": 300,
    "expected_status_code": 200
}
```

#### 2. List Monitored Sites
```http
GET /sites
```

#### 3. Get Site History
```http
GET /sites/{site_id}/history
```

#### 4. Delete Site
```http
DELETE /sites/{site_id}
```

#### 5. Add Discord Webhook
```http
POST /webhook
```
Request body:
```json
{
    "url": "https://discord.com/api/webhooks/...",
    "name": "My Channel"
}
```

## Design Decisions

### Architecture Overview

The application follows a modular architecture with clear separation of concerns:

1. **API Layer** (`main.py`)
   - Handles HTTP requests
   - Input validation
   - Route management

2. **Data Layer** (`models.py`, `database.py`)
   - SQLite database
   - SQLAlchemy ORM
   - Data models and relationships

3. **Monitoring Service** (`monitor.py`)
   - Background website checking
   - Status tracking
   - Response time measurement

4. **Notification Service** (`discord.py`)
   - Discord webhook management
   - Notification formatting
   - Error handling

### Key Design Choices

1. **Background Processing**
   - Used threading for simplicity and efficiency
   - Each website check runs independently
   - Non-blocking architecture

2. **Database Design**
   - Separate tables for websites, status checks, and webhooks
   - Indexed fields for efficient queries
   - Timestamp tracking for status changes

3. **Error Handling**
   - Comprehensive error catching
   - Detailed error messages
   - Automatic retry mechanism

4. **Scalability Considerations**
   - Modular design for easy scaling
   - Independent monitoring threads
   - Configurable check intervals



## Sample Discord Notifications

### Recovery Example
```
🟢 Website Recovery Alert
Site: Apple (https://www.apple.com/)
Status: UP
Time: 2025-01-17 09:41:56 UTC
Response Time: 416.13ms
Today at 3:11 PM
```

### Downtime Example
```
🔴 Website Down Alert
Site: Test Down Site (https://nonexistent-website-test.com/)
Status: DOWN
Time: 2025-01-17 09:55:09 UTC
Error: HTTPSConnectionPool(host='nonexistent-website-test.com', port=443): 
      Max retries exceeded with url: / (Caused by NameResolutionError(
      "<urllib3.connection.HTTPSConnection object at 0x000002447F9896D0>: 
      Failed to resolve 'nonexistent-website-test.com' 
      ([Errno 11001] getaddrinfo failed)"))
Today at 3:25 PM
```



## Testing

Run tests using pytest:
```bash
pytest tests/test_monitor.py
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Error Handling

The system handles various error scenarios:
- Network timeouts
- DNS resolution failures
- Invalid URLs
- Discord webhook failures
- Database connection issues

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)
