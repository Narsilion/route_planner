import configparser
import os
import sys
import flask

real_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(real_path + '/../.')

from flaskr import app
from flaskr.implementation import tools

config = configparser.ConfigParser()


@app.route('/get_all_for_current', methods=['GET', 'OPTIONS'])
def get_all_for_current():
    """Returns all possible variants from the current location
    Example:
    curl http://localhost:5000/get_all_for_current?origin=LED&destination=CPH&one_way=true
    Taken from:
    http://map.aviasales.ru/supported_directions.json?origin_iata=LED&one_way=false&locale=ru
    """

    origin = flask.request.args.get('origin')
    destination = flask.request.args.get('destination')
    one_way = flask.request.args.get('one_way')
    one_way = 'false' if not one_way or one_way == 'false' else 'true'

    # Send request
    request_data = {'origin_iata': origin, 'one_way': one_way, 'locale': 'ru'}
    result = tools.send_request('map.aviasales.ru', 'supported_directions.json', request_data)

    directions = result["directions"]

    our_direction = None
    for direction in directions:
        if direction['iata'] == destination:
            our_direction = direction

    return flask.json.dumps(our_direction, indent=2)


@app.route('/get_price_calendar', methods=['GET', 'OPTIONS'])
def get_best_price_calendar():
    """Returns all possible variants from the current location
    Example:
    curl 'http://localhost:5000/get_best_price_calendar?origin=LED&destination=CPH&one_way=true&depart_date=2019-01-05'
    Taken from:
    http://min-prices.aviasales.ru/calendar_preload?origin=LED&destination=CPH&depart_date=2019-01-05&one_way=true
    """

    origin = flask.request.args.get('origin')
    depart_date = flask.request.args.get('depart_date')
    destination = flask.request.args.get('destination')
    one_way = flask.request.args.get('one_way')
    one_way = 'false' if not one_way or one_way == 'false' else 'true'

    # Send request
    request_data = {'origin': origin, 'destination': destination, 'depart_date': depart_date, 'one_way': one_way}
    result = tools.send_request('min-prices.aviasales.ru', 'calendar_preload', request_data)

    if not result['errors']:
        final_result = []

        # For some reason 'depart_date' parameter is ignored by Aviasales, so we parse it here
        for direction in result['best_prices']:
            if depart_date == direction['depart_date']:
                app.logger.debug(direction['depart_date'])
                final_result.append(direction)
    else:
        final_result = result['errors']

    return flask.json.dumps(final_result, indent=2)


@app.route('/get_prices', methods=['GET', 'OPTIONS'])
def get_prices():
    """Returns all possible variants from the current location
    Example:
    curl 'http://localhost:5000/get_prices?origin=LED&destination=CPH&one_way=true&beginning_of_period=2019-01-01&trip_duration=3'
    Taken from:
    http://api.travelpayouts.com/v2/prices/latest?currency=rub&period_type=year&page=1&limit=30&show_to_affiliates=true
    &sorting=price&token=<your token>
    """

    origin = flask.request.args.get('origin')
    beginning_of_period = flask.request.args.get('beginning_of_period')
    destination = flask.request.args.get('destination')
    one_way = flask.request.args.get('one_way')
    one_way = 'false' if not one_way or one_way == 'false' else 'true'
    app.logger.debug(app.config)

    # Send request
    config.read_file(open(os.path.join(app.instance_path, 'common.cfg')))
    token = config.get('DEFAULT', 'aviasales_token')
    request_data = {'show_to_affiliates': 'false', 'origin': origin, 'destination': destination,
                    'beginning_of_period': beginning_of_period, 'one_way': one_way, 'period_type': 'month',
                    'token': token}

    result = tools.send_request('api.travelpayouts.com', 'v2/prices/latest', request_data)

    # if not result['errors']:
    #     final_result = []
    #
    #     # For some reason 'depart_date' parameter is ignored by Aviasales, so we parse it here
    #     for direction in result['best_prices']:
    #         if depart_date == direction['depart_date']:
    #             app.logger.debug(direction['depart_date'])
    #             final_result.append(direction)
    # else:
    #     final_result = result['errors']

    return flask.json.dumps(result, indent=2)
