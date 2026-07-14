"""Prototype REST API for programmatic scraper access."""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from scraper import ScraperPro, SubscriptionTier
import logging
from functools import wraps
from pathlib import Path
import os

app = Flask(__name__)
allowed_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:8501").split(",")
    if origin.strip()
]
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
scraper_app = ScraperPro()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def require_api_key(f):
    """Decorator to validate API key and check API access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        client = scraper_app.client_manager.verify_api_key(api_key)
        
        if not client:
            return jsonify({'error': 'Invalid API key'}), 401
        
        if not client.active:
            return jsonify({'error': 'Account inactive'}), 403
        
        # Check if tier has API access
        tier_info = SubscriptionTier[client.tier].value
        if not tier_info.get('api_access', False):
            return jsonify({
                'error': 'API access not available on your plan',
                'upgrade_required': True,
                'current_tier': client.tier
            }), 403
        
        # Add client to request context
        request.client = client
        return f(*args, **kwargs)
    
    return decorated_function


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'ScraperPro API'})


@app.route('/api/v1/account', methods=['GET'])
@require_api_key
def get_account_info():
    """Get account information"""
    client = request.client
    tier_info = SubscriptionTier[client.tier].value
    
    return jsonify({
        'client_id': client.client_id,
        'name': client.name,
        'email': client.email,
        'tier': client.tier,
        'tier_features': {
            'max_requests_per_day': tier_info['max_requests_per_day'],
            'max_configs': tier_info['max_configs'],
            'export_formats': tier_info['export_formats']
        },
        'usage': {
            'requests_today': client.requests_today,
            'requests_remaining': scraper_app._get_remaining_requests(client)
        },
        'created_at': client.created_at
    })


@app.route('/api/v1/configs', methods=['GET'])
@require_api_key
def list_configs():
    """List all configurations for the client"""
    client = request.client
    config_dir = Path('data/configs')
    
    configs = []
    for config_file in config_dir.glob(f'{client.client_id}_*.json'):
        with open(config_file, 'r') as f:
            import json
            config_data = json.load(f)
            configs.append({
                'config_id': config_data['config_id'],
                'name': config_data['name'],
                'target_url': config_data['target_url'],
                'output_format': config_data['output_format'],
                'active': config_data.get('active', True)
            })
    
    return jsonify({
        'count': len(configs),
        'configs': configs
    })


@app.route('/api/v1/scrape', methods=['POST'])
@require_api_key
def execute_scrape():
    """Execute a scraping job"""
    client = request.client
    data = request.get_json()
    
    if not data or 'config_id' not in data:
        return jsonify({'error': 'config_id required'}), 400
    
    config_id = data['config_id']
    
    # Execute scrape
    result = scraper_app.execute_scrape(client.api_key, config_id)
    
    if result['success']:
        return jsonify({
            'success': True,
            'job_id': f"{client.client_id}_{config_id}_{int(time.time())}",
            'records': result['records'],
            'output_file': result['output_file'],
            'requests_remaining': result['requests_remaining']
        }), 200
    else:
        status_code = 429 if 'rate limit' in result['error'].lower() else 400
        return jsonify({
            'success': False,
            'error': result['error']
        }), status_code


@app.route('/api/v1/download/<path:filename>', methods=['GET'])
@require_api_key
def download_file(filename):
    """Download a result file"""
    client = request.client
    
    # Security: Ensure client can only access their own files
    if not filename.startswith(client.client_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    file_path = Path('output') / filename
    
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True)


@app.route('/api/v1/results', methods=['GET'])
@require_api_key
def list_results():
    """List all result files for the client"""
    client = request.client
    output_dir = Path('output')
    
    results = []
    for result_file in output_dir.glob(f'{client.client_id}_*'):
        if result_file.suffix in ['.csv', '.xlsx', '.json']:
            results.append({
                'filename': result_file.name,
                'size_kb': result_file.stat().st_size / 1024,
                'created_at': result_file.stat().st_mtime,
                'format': result_file.suffix[1:],
                'download_url': f'/api/v1/download/{result_file.name}'
            })
    
    # Sort by creation time (newest first)
    results.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'count': len(results),
        'results': results
    })


@app.route('/api/v1/webhook', methods=['POST'])
@require_api_key
def register_webhook():
    """Register webhook for scraping completion notifications"""
    client = request.client
    data = request.get_json()
    
    if not data or 'webhook_url' not in data:
        return jsonify({'error': 'webhook_url required'}), 400
    
    # TODO: Save webhook configuration
    # This is a placeholder for webhook functionality
    
    return jsonify({
        'success': True,
        'message': 'Webhook registered',
        'webhook_url': data['webhook_url']
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Create necessary directories
    Path('logs').mkdir(exist_ok=True)
    Path('output').mkdir(exist_ok=True)
    Path('data/clients').mkdir(parents=True, exist_ok=True)
    Path('data/configs').mkdir(parents=True, exist_ok=True)
    
    # Run server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
