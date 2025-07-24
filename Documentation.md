# URL Shortener Service Documentation

## Overview
This service provides a simple API to shorten URLs, redirect using a short code, and view analytics for each short code. All data is stored in memory and is lost when the server restarts. The project is implemented in Python using Flask.

---

## How it Works
- **Shorten URLs:** Accepts a long URL and returns a short code and short URL.
- **Redirect:** Redirects to the original URL when the short code is accessed.
- **Analytics:** Provides click count and creation timestamp for each short code.
- **Thread Safety:** All operations on the in-memory store are thread-safe.

---

## API Endpoints

### 1. Shorten URL
- **POST /api/shorten**
- **Request Body:**
  ```json
  { "url": "https://www.example.com/very/long/url" }
  ```
- **Response:**
  ```json
  { "short_code": "abc123", "short_url": "http://localhost:5000/abc123" }
  ```
- **Errors:**
  - 400: Missing or invalid URL
  - 500: Could not generate unique short code

### 2. Redirect
- **GET /<short_code>**
- **Behavior:** Redirects to the original URL if the code exists, increments click count.
- **Errors:**
  - 404: Short code not found

### 3. Analytics
- **GET /api/stats/<short_code>**
- **Response:**
  ```json
  { "url": "https://www.example.com/very/long/url", "clicks": 5, "created_at": "2024-01-01T10:00:00" }
  ```
- **Errors:**
  - 404: Short code not found

### 4. Health Checks
- **GET /**
- **GET /api/health**
- Returns service status.

---

## Design Decisions & Notes
- **Thread Safety:** All access to the in-memory store is protected by a lock to ensure safe concurrent requests.
- **Error Handling:** All endpoints use try/except and log errors to `error.log` for debugging. Clear error messages are returned for invalid input and server errors.
- **Short Code Generation:** Generates a random 6-character alphanumeric code. Retries up to 5 times to avoid collisions.
- **URL Validation:** Only accepts URLs with http/https scheme and a valid netloc.
- **Extensibility:** The code is organized for easy extension (e.g., adding persistent storage, custom codes, or expiration).

---

## Test Coverage
- All endpoints and error cases are tested, including:
  - Shortening valid, invalid, empty, and very long URLs
  - Redirecting and analytics
  - Non-existent codes
  - Shortening the same URL multiple times
- Tests are written using pytest and can be run with `pytest` from the project directory.

---

## Example API Usage

```bash
# Shorten a URL
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url"}'

# Response: {"short_code": "abc123", "short_url": "http://localhost:5000/abc123"}

# Use the short URL (this redirects)
curl -L http://localhost:5000/abc123

# Get analytics
curl http://localhost:5000/api/stats/abc123

# Response: {"url": "https://www.example.com/very/long/url", "clicks": 5, "created_at": "2024-01-01T10:00:00"}
```

---

## How to Run Tests
1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `pytest`

---
I have Used AI tools for clear Comments for the Codebase.