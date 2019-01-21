import configparser
import os
import requests

from flaskr import app


def send_request(domain, func_name, request_data):
    """
    Sends a request to the given URL with the provided request data
    :param domain:
    :param func_name:
    :param request_data:
    :return:
    """
    url = 'http://%s/%s' % (domain, func_name)
    app.logger.debug(request_data)

    r = requests.get(url, request_data)

    return r.json()


def check_dest_supported(orig_list, destination):
    """Checks if the given destination is supported for the given origin
    :return: dictionary with origins and a False or True depending on whether the destination is supported or not
    Taken from:
    http://map.aviasales.ru/supported_directions.json?origin_iata=LED&one_way=false&locale=ru
    """

    dest_support_dict = dict()

    for origin in orig_list:
        # Send request
        request_data = {'origin_iata': origin, 'one_way': 'true', 'locale': 'ru'}
        result = send_request('map.aviasales.ru', 'supported_directions.json', request_data)

        directions = result["directions"]

        is_supported = False
        for direction in directions:
            if direction['iata'] == destination:
                is_supported = True
        dest_support_dict[origin] = is_supported

    return dest_support_dict


# def get_additional_origins(origin, destination):
#     """Returns a list of possible origin airports users can fly from"""
#     # TODO: Here will be a request to some database in the future
#
#     orig_list = []
#     if origin == 'LED':
#         orig_list = [origin, 'MOW', 'HEL']
#     elif origin == 'MOW':
#         orig_list = [origin, 'LED']
#
#     # Check if destination is supported
#     dest_support_dict = check_dest_supported(orig_list, destination)
#
#     sup_orig_list = [origin for origin in dest_support_dict if dest_support_dict[origin]]
#
#     return sup_orig_list


def get_autocomplete_value(city):
    request_data = {'term': city, 'locale': 'en', 'types': 'city'}
    result = send_request('autocomplete.travelpayouts.com', 'places2', request_data)

    code_list = []
    for d in result:
        code = d['code']
        code_list.append(code)

    return code_list


def get_origins(origin, destination):
    """Returns a list of nearest airports to the origin airport"""

    config = configparser.ConfigParser()
    config.read_file(open(os.path.join(app.instance_path, 'common.cfg')))
    token = config.get('DEFAULT', 'aviasales_token')

    request_data = {'currency': 'rub', 'origin': origin, 'show_to_affiliates': 'false', 'token': token,
                    'destination': destination}
    result = send_request('api.travelpayouts.com', 'v2/prices/nearest-places-matrix', request_data)

    if 'message' in result:
        return result

    origins = result['data']['origins']
    all_origins = get_additional_origins(origin, origins, destination)

    return all_origins


def get_additional_origins(origin, aviasales_origins, destination):
    """Returns a list of possible origin airports users can fly from"""
    # TODO: Here will be a request to some database in the future

    orig_list = []
    if origin == 'LED':
        orig_list = [origin, 'MOW', 'HEL']
    elif origin == 'MOW':
        orig_list = [origin, 'LED']

    # Check if destination is supported
    dest_support_dict = check_dest_supported(orig_list, destination)

    sup_orig_list = [origin for origin in dest_support_dict if dest_support_dict[origin]]
    sup_orig_list.extend(aviasales_origins)

    return sup_orig_list
