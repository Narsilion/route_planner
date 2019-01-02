import requests


def send_request(func_name, args):

    domain = 'map.aviasales.ru'
    url = 'http://%s/%s' % (domain, func_name)

    request_data = {'origin_iata': args['origin'], 'one_way': 'false', 'locale': 'ru'}
    print(request_data)

    r = requests.get(url, request_data)

    return r.json()

