__author__ = 'BenjaminHabert'

import os
import csv
import json
from math import pi

insee_data = {}
insee_data_top = {}

def _load_data():
    """ Loads csv data
    :return: nothing
    """
    dirname = 'data'
    filename = 'Codes-INSEE-communes-geolocalisees.csv'
    path_here = os.path.dirname(__file__)
    path_to_data = os.path.join(path_here, dirname, filename)
    print('[insee.py] Loading list of insee codes from {:s}'.format(filename))
    # with open(path_to_data, encoding='latin1') as f:  # THIS DOES NOT WORK WITH PYTHON 2.7
    with open(path_to_data) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            _clean_csv_dict(row)
            insee_data[row['Insee']] = row

    #select top cities from this
    populations = [(v['Insee'], v['pop99']) for v in insee_data.values()]
    populations.sort(reverse=True, key=lambda x: x[1])
    for insee_code, pop in populations[0:200]:
        insee_data_top[insee_code] = insee_data[insee_code]



def _clean_csv_dict(d):
    """ Cleans data read from csv file, inplace

    :param d: dict that is modified in place
    :return: nothing
    """
    try:
        d["Nom"] = d["Nom"].decode('latin1')
        d['Insee'] = format_insee_code(d['Insee'])
        d['pop99'] = int(d['pop99'])


        d['location'] = [float(d['latitude_radian'])*180/pi, float(d['longitude_radian'])*180/pi]
        d.pop('longitude_radian', None)
        d.pop('latitude_radian', None)

        for s in ['surface', 'Altitude'] :
            try:
                d[s] = float(d[s])
            except Exception :
                d[s] = 0.0
        d['code_postal'] = format_insee_code(d['code_postal'])
    except Exception as e:
        print(e)
        print(d)


def format_insee_code(code):
    try:
        return '{:05d}'.format(int(code))
    except Exception:
        return code

def get_city_data(insee_code):
    """ Return dictionary of city data from insee code

    :param insee_code: int or str of insee code ( "75000" or 75000 )
    :return: dict with following format :
        {
           "Nom": "Paris",
           "Insee": "75056",
           "code_postal": "75000",
           "pop99": 2125246,
           "Altitude": 60.0,
           "location": [
              2.3457999087116095,
              48.86080170979514
           ],
           "surface": 105.63
        }
        location is [latitiude, longitude] in degrees
        surface is square km
        Altitude is meters

        some cities have several code_postal:  "03034|03035"
        Insee is a unique identifier and is allways a 5-character string. It can contain letters in some rare cases
    """
    insee_code = format_insee_code(insee_code)
    if insee_code in insee_data.keys():
        return insee_data[insee_code]
    else:
        return {}

_load_data()

if __name__ == '__main__':
    print('This is the insee.py file of insee submodule')