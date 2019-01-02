import os
import sys
import flask

real_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(real_path + '/../.')

from flaskr import app
from flaskr.implementation import tools


@app.route('/get_all_for_current', methods=['GET', 'OPTIONS'])
def test():
    """Returns all possible variants from the current location
    Example:
    curl http://localhost:5000/get_all_for_current?origin=LED&target=CPH&one_way=true
    """
    # http://map.aviasales.ru/supported_directions.json?origin_iata=LED&one_way=false&locale=ru

    origin = flask.request.args.get('origin')
    target = flask.request.args.get('target')
    one_way = flask.request.args.get('one_way')

    # Send request
    result = tools.send_request('supported_directions.json', {'origin': origin})

    directions = result["directions"]

    our_direction = None
    for direction in directions:
        app.logger.debug(direction['iata'])
        if direction['iata'] == target:
            our_direction = direction

    return flask.json.dumps(our_direction, indent=2)
