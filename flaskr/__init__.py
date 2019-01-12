import os
import sys
import flask
import logging

real_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(real_path + '/../.')

log_path = os.path.join(os.environ['HOME'], 'logs/aero_route_planner', 'service.log')
logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(asctime)s %(message)s')


# create and configure the app
app = flask.Flask(__name__, instance_relative_config=True, instance_path='/home/aartemov/aero_planner_configs')

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

import flaskr.views.main


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
