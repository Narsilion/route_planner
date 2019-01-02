import os
import sys
import flask
import logging

real_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(real_path + '/../.')

log_path = os.path.join(os.environ['HOME'], 'logs/aero_route_planner', 'service.log')
logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s %(message)s')


# create and configure the app
app = flask.Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py', silent=True)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

import flaskr.views.main
import flaskr.views.view1


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
