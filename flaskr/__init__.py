import os
import sys
import flask
import logging
from pathlib import Path

# Setup paths
real_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(real_path + '/../.')

# Container-friendly configuration
APP_ENV = os.environ.get('FLASK_ENV', 'production')
APP_DEBUG = APP_ENV == 'development'

# Use /app/data for instance path (writable in container)
data_dir = Path('/app/data')
data_dir.mkdir(parents=True, exist_ok=True)

log_dir = data_dir / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

# Setup logging
log_file = log_dir / 'app.log'
logging.basicConfig(
    filename=str(log_file),
    level=logging.DEBUG if APP_DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create Flask app
app = flask.Flask(__name__, instance_relative_config=True, instance_path=str(data_dir))

# App configuration
app.config['JSON_SORT_KEYS'] = False
app.config['ENV'] = APP_ENV
app.config['DEBUG'] = APP_DEBUG

# Ensure data directory exists
data_dir.mkdir(parents=True, exist_ok=True)

# Import routes
import flaskr.views.main


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=APP_DEBUG)
