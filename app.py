from flask import Flask, request, render_template
import datetime
import json
import sys

app = Flask(__name__)

@app.route('/')
def index():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return render_template('index.html', user_ip=user_ip)

@app.route('/log_ip', methods=['POST'])
def log_ip():
    # Get user IP and timestamp
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    timestamp = datetime.datetime.utcnow().isoformat()
    
    # Log to stdout with flush
    log_entry = {
        'ip': user_ip,
        'timestamp': timestamp,
        'user_agent': request.headers.get('User-Agent')
    }
    print(json.dumps(log_entry), flush=True)
    
    return render_template('index.html', user_ip=user_ip, message="IP and login time captured successfully!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)