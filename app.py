from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from timezonefinder import TimezoneFinder
import pytz
import json
from datetime import datetime
import os
import requests
from main import run_kp_analysis  # Ensure this import works in production

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
DATA_DIR = os.path.join(os.getcwd(), 'user_data')  # Explicit path for production
API_ENDPOINTS = [
    {'url': 'https://api.vedicastroapi.com/v3-json/dashas/maha-dasha', 'filename': 'input_kp_mahadasha_details.json'},
    {'url': 'https://api.vedicastroapi.com/v3-json/dashas/antar-dasha', 'filename': 'input_kp_antardasha_details.json'},
    {'url': 'https://api.vedicastroapi.com/v3-json/dashas/paryantar-dasha', 'filename': 'input_kp_paryantardasha_details.json'},
    {'url': 'https://api.vedicastroapi.com/v3-json/extended-horoscope/kp-houses', 'filename': 'input_kp_house_details.json'},
    {'url': 'https://api.vedicastroapi.com/v3-json/extended-horoscope/kp-planets', 'filename': 'input_kp_planet_details.json'},
    {'url': 'https://api.vedicastroapi.com/v3-json/horoscope/planet-details', 'filename': 'input_kp_planet_position_details.json'},
    {'url': 'https://api.vedicastroapi.com/v3-json/extended-horoscope/yoga-list', 'filename': 'input_kp_list_of_yogas_details.json'}
]

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

def call_api(endpoint, params):
    """Generic API call handler"""
    try:
        response = requests.get(
            endpoint['url'],
            params=params,
            timeout=10
        )
        response.raise_for_status()
        
        filepath = os.path.join(DATA_DIR, endpoint['filename'])
        with open(filepath, 'w') as f:
            json.dump(response.json(), f, indent=2)
            
        return {'status': 'success', 'filename': endpoint['filename']}
    except Exception as e:
        return {'status': 'error', 'filename': endpoint['filename'], 'message': str(e)}

@app.route('/generate-params', methods=['POST'])
def generate_params():
    try:
        data = request.json
        
        # Validate input
        required_fields = ['dob', 'tob', 'lat', 'lon']
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        # Calculate timezone offset
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=data['lon'], lat=data['lat'])
        timezone = pytz.timezone(timezone_str)
        offset = timezone.utcoffset(datetime.now()).total_seconds() / 3600

        # Prepare API parameters
        params = {
            'dob': data['dob'],
            'tob': data['tob'],
            'lat': data['lat'],
            'lon': data['lon'],
            'tz': offset,
            'api_key': os.environ.get('VEDIC_API_KEY', '6a799635-5162-574a-970e-5d3c931c6de6'),  # Use environment variable
            'lang': 'en'
        }

        # Call all APIs
        results = []
        for endpoint in API_ENDPOINTS:
            results.append(call_api(endpoint, params))

        # Check for API errors
        success_count = sum(1 for r in results if r['status'] == 'success')
        if success_count != len(API_ENDPOINTS):
            return jsonify({
                "status": "error",
                "message": f"Only {success_count}/7 files created",
                "details": results
            }), 400

        # Run KP analysis
        analysis_result = run_kp_analysis()
        if analysis_result['status'] != 'success':
            raise Exception(analysis_result['message'])

        return jsonify({
            "status": "success",
            "message": "Full analysis completed",
            "output_file": analysis_result['output_file'],
            "generated_files": analysis_result['generated_files']
        })

    except Exception as e:
        app.logger.error(f"Error in generate-params: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))  # Render provides PORT environment variable
    app.run(host='0.0.0.0', port=port, debug=False)  # Debug=False for production