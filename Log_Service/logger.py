from flask import Flask, request, jsonify
import logging
import os
import re
import json

from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# Set up logging file
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

# Set up logging with timestamp and timezone
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %Z'
)

# Disable unnecessary logging by Flask and Werkzeug
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True


@app.route('/log', methods=['POST'], strict_slashes=False)
def logger():
    ''' Accepts log messages, identfies service, log type and adds log'''
    data = request.json
    message = data.get('message')
    level = data.get('level', 'info').lower()

    # Get the Docker domain from the request headers to identify microservice
    docker_domain = request.headers.get('X-Docker-Domain')

    # Include the Docker domain in the log message
    if docker_domain:
        message = f'[{docker_domain}]: {message}'

    # Log the message at the specified level
    if level == 'debug':
        logging.debug(message)
    elif level == 'info':
        logging.info(message)
    elif level == 'warning':
        logging.warning(message)
    elif level == 'error':
        logging.error(message)
    elif level == 'critical':
        logging.critical(message)
    else:
        return f'Invalid log level: {level}', 400
    return 'Message logged successfully', 200


@app.route('/', methods=['GET'], strict_slashes=False)
def get_logs():
    ''' Returns the specified number of log entries'''
    entries = int(request.args.get('entries', 10))

    with open(log_file, 'r', encoding='utf-8') as lf_io:
        lines = lf_io.readlines()

    # Get the last n lines from the log file
    logs = []
    count = 0
    for line in lines[::-1]:
        if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line):
            count += 1
            if count > entries:
                break
            logs.append(line)
        else:
            logs.append(line)

    # return logs entries as strings (new line already added)
    return ''.join(reversed(logs))


# Swagger documentation Endpoint
@app.route('/swagger.json')
def swagger_json():
    with app.open_resource('swagger.json') as f:
        swagger_data = json.load(f)
    return jsonify(swagger_data)


# Create a Swagger blueprint
SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'
swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Log Service"
    }
)
app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.environ.get('DEBUG'))
