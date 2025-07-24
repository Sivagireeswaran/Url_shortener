import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the root health check endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'URL Shortener API'

def test_shorten_and_redirect_and_stats(client):
    """Test shortening a valid URL, redirecting, and getting analytics."""
    long_url = "https://www.example.com/abc"
    resp = client.post('/api/shorten', json={"url": long_url})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "short_code" in data
    assert "short_url" in data
    short_code = data["short_code"]

    # Redirect using the short code
    resp = client.get(f'/{short_code}', follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"] == long_url

    # Get analytics for the short code
    resp = client.get(f'/api/stats/{short_code}')
    assert resp.status_code == 200
    stats = resp.get_json()
    assert stats["url"] == long_url
    assert stats["clicks"] == 1  # One redirect above
    assert "created_at" in stats

def test_shorten_invalid_url(client):
    """Test shortening an invalid URL (should return 400)."""
    resp = client.post('/api/shorten', json={"url": "not-a-url"})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data

def test_stats_nonexistent_code(client):
    """Test getting stats for a non-existent short code (should return 404)."""
    resp = client.get('/api/stats/doesnotexist')
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data

def test_shorten_empty_url(client):
    """Test shortening an empty URL (should return 400)."""
    resp = client.post('/api/shorten', json={"url": ""})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data

def test_shorten_very_long_url(client):
    """Test shortening a very long URL (should succeed if valid)."""
    long_url = "https://www.example.com/" + "a" * 2000
    resp = client.post('/api/shorten', json={"url": long_url})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "short_code" in data
    assert "short_url" in data

def test_shorten_same_url_multiple_times(client):
    """Test shortening the same URL multiple times (should return different codes)."""
    long_url = "https://www.example.com/repeat"
    codes = set()
    for _ in range(3):
        resp = client.post('/api/shorten', json={"url": long_url})
        assert resp.status_code == 201
        data = resp.get_json()
        codes.add(data["short_code"])
    assert len(codes) == 3  # Should be different codes each time