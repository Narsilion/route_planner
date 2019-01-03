import requests

from flaskr import app


def send_request(domain, func_name, request_data):

    # domain = 'map.aviasales.ru'
    url = 'http://%s/%s' % (domain, func_name)

    # request_data = {'origin_iata': args['origin'], 'one_way': 'false', 'locale': 'ru'}
    app.logger.debug(request_data)

    r = requests.get(url, request_data)

    return r.json()

