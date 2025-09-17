# Qbus Scraper

A web scraper that monitors a Qbus dashboard page and provides the data via a REST API.

## Features

- Opens the Qbus dashboard page on startup and keeps it open in the background
- Receives live updates over websockets from the page
- Provides a Flask HTTP server with endpoints to access scraped data
- Automatic browser reload every hour to prevent memory leaks
- Basic authentication for API endpoints

## Project Structure

```
qbus-scraper/
├── src/scraper/
│   ├── __init__.py        # Package initialization
│   ├── app.py             # Flask web server and API endpoints
│   ├── config.py          # Configuration settings
│   ├── run.py             # Application startup logic and entry point
│   └── scraper.py         # Browser management and scraping logic
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
└── docker-compose.yml    # Multi-container setup
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start a Selenium server (using Docker):
   ```bash
   docker run -p 4444:4444 --name selenium selenium/standalone-chrome:latest
   ```

3. Run the scraper:
   ```bash
   python src/scraper/run.py
   ```

## API Endpoints

### GET /data

Scrapes the current page and returns the data.

**Authentication:** Basic Auth (username: `admin`, password: `password`)

**Response:**
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "url": "https://qbuscontrol.com/app/tabs/dashboard",
  "title": "Qbus Dashboard",
  "data": {
    "tiles": [
      {
        "name": "Sensor Name",
        "value": "25.5°C",
        "element": "<ccl-icon1x1>...</ccl-icon1x1>"
      }
    ]
  }
}
```

### GET /health

Health check endpoint to verify the scraper is running.

**Response:**
```json
{
  "status": "healthy",
  "browser_initialized": true,
  "last_reload": "2024-01-01T12:00:00",
  "timestamp": "2024-01-01T12:00:00"
}
```

### POST /reload

Force reload the browser (useful for troubleshooting).

**Authentication:** Basic Auth (username: `admin`, password: `password`)

## Configuration

The scraper can be configured using environment variables:

- `SELENIUM_HOST`: Selenium server host (default: `selenium:4444`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `BASIC_AUTH_USERNAME`: Username for API authentication (required)
- `BASIC_AUTH_PASSWORD`: Password for API authentication (required)
- `QBUS_USERNAME`: Username for Qbus dashboard login (required)
- `QBUS_PASSWORD`: Password for Qbus dashboard login (required)

See `env.example` for a complete example.

## Docker

The project includes a `docker-compose.yml` file for easy deployment:

```bash
docker-compose up -d
```

This will start both the Selenium server and the scraper application.
