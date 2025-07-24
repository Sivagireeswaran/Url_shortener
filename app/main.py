from flask import Flask, jsonify, request
from .models import url_store
from .utils import generate_short_code, is_valid_url
import logging

app = Flask(__name__)

# Set up error logging
logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(message)s')

@app.route('/')
def health_check():
    """Health check endpoint for the root URL."""
    return jsonify({
        "status": "healthy",
        "service": "URL Shortener API"
    })

@app.route('/api/health')
def api_health():
    """Health check endpoint for the API."""
    return jsonify({
        "status": "ok",
        "message": "URL Shortener API is running"
    })

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    """Shorten a given URL. Accepts JSON with 'url', validates, generates a short code, and returns it."""
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({"error": "Missing 'url' in request body"}), 400
        long_url = data['url']
        if not is_valid_url(long_url):
            return jsonify({"error": "Invalid URL"}), 400
        # Generate a unique short code, retrying up to 5 times to avoid collision
        for _ in range(5):
            short_code = generate_short_code()
            if not url_store.get_url(short_code):
                break
        else:
            return jsonify({"error": "Could not generate unique short code"}), 500
        url_store.add_url(short_code, long_url)
        short_url = request.host_url.rstrip('/') + '/' + short_code
        return jsonify({"short_code": short_code, "short_url": short_url}), 201
    except Exception as e:
        # Log unexpected errors for debugging
        logging.error(f"Error in /api/shorten: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/<short_code>', methods=['GET'])
def redirect_short_url(short_code):
    """Redirect to the original URL for a given short code. Increments click count."""
    try:
        entry = url_store.get_url(short_code)
        if not entry:
            return jsonify({"error": "Short code not found"}), 404
        url_store.increment_click(short_code)
        return '', 302, {'Location': entry['url']}
    except Exception as e:
        # Log unexpected errors for debugging
        logging.error(f"Error in /<short_code>: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/stats/<short_code>', methods=['GET'])
def get_stats(short_code):
    """Return analytics for a given short code: original URL, click count, and creation timestamp."""
    try:
        stats = url_store.get_stats(short_code)
        if not stats:
            return jsonify({"error": "Short code not found"}), 404
        return jsonify(stats)
    except Exception as e:
        # Log unexpected errors for debugging
        logging.error(f"Error in /api/stats/<short_code>: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)