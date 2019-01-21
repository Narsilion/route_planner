import configparser
import os
import sys
import flask

real_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(real_path + '/../.')

from flaskr import app
from flaskr.implementation import tools

config = configparser.ConfigParser()


@app.route('/get_iata', methods=['GET', 'OPTIONS'])
def get_iata():
    """Returns iata code of the given location location
    Example:
    curl 'http://localhost:5000/get_iata?origin=Москва&destination=Лондон'
    Taken from:
    https://www.travelpayouts.com/widgets_suggest_params?q=Из%20Москвы%20в%20Лондон
    """

    origin = flask.request.args.get('origin')
    destination = flask.request.args.get('destination')

    q = 'Из %s в %s' % (origin, destination)
    request_data = {'q': q}
    result = tools.send_request('www.travelpayouts.com', 'widgets_suggest_params', request_data)

    return flask.json.dumps(result, indent=2)


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
                final_result.append(direction)
    else:
        final_result = result['errors']

    return flask.json.dumps(final_result, indent=2)


@app.route('/get_prices', methods=['GET', 'OPTIONS'])
def get_prices():
    """Returns all possible variants for the given destination
    Example:
    curl 'http://localhost:5000/get_prices?origin=Saint&destination=Copen&one_way=true&beginning_of_period=2019-01-01&trip_duration=3
    Taken from:
    http://api.travelpayouts.com/v2/prices/latest?currency=rub&period_type=year&page=1&limit=30&show_to_affiliates=true
    &sorting=price&token=<your token>
    """

    origin = flask.request.args.get('origin')
    beginning_of_period = flask.request.args.get('beginning_of_period')
    destination = flask.request.args.get('destination')
    one_way = flask.request.args.get('one_way')
    one_way = 'false' if not one_way or one_way == 'false' else 'true'

    origin_iata = tools.get_autocomplete_value(origin)[0]
    dest_iata = tools.get_autocomplete_value(destination)[0]
    # sup_orig_list = tools.get_orig_list(origin_iata, dest_iata)

    sup_orig_list = tools.get_origins(origin_iata, dest_iata)

    if 'message' in sup_orig_list:
        return flask.json.dumps(sup_orig_list['message'])

    result_dict = dict()
    if sup_orig_list:
        for sup_origin in sup_orig_list:
            # Send request
            config.read_file(open(os.path.join(app.instance_path, 'common.cfg')))
            token = config.get('DEFAULT', 'aviasales_token')
            request_data = {'show_to_affiliates': 'false', 'origin': sup_origin, 'destination': dest_iata,
                            'beginning_of_period': beginning_of_period, 'one_way': one_way, 'period_type': 'month',
                            'token': token}

            result = tools.send_request('api.travelpayouts.com', 'v2/prices/latest', request_data)

            if 'message' in result:
                return flask.json.dumps(result['message'])

            result_dict[sup_origin] = (result['data'])

        comp_dict = {}
        tmp_dict_list = []
        tmp_dict = dict()
        for origin, variant_list in result_dict.items():
            vars_dict = dict()
            for variant in variant_list:
                dep_date = variant['depart_date']
                vars_dict[dep_date] = {origin: {'number_of_changes': variant['number_of_changes'],
                                                'price': variant['value'], 'duration': variant['duration']}}
            tmp_dict[origin] = vars_dict
            tmp_dict_list.append(vars_dict)

        for d in tmp_dict_list:
            for k, v in d.items():
                if k not in comp_dict:
                    comp_dict[k] = v
                else:
                    keys = list(v)
                    comp_dict[k][keys[0]] = v[keys[0]]

        return flask.json.dumps(comp_dict, indent=2)
    else:
        return flask.json.dumps("The destination '%s' is not supported for origin '%s'" % (origin, destination))
