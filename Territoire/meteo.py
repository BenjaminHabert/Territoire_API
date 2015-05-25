__author__ = 'BenjaminHabert'
import os
import pandas as pd
import numpy as np
import csv
import datetime
import math
from . import insee

import json

# https://donneespubliques.meteofrance.fr/?fond=donnee_libre&prefixe=Txt%2FSynop%2FArchive%2Fsynop&extension=csv.gz&date=201302


def _load_data():
    """ Loads csv data
    :return: data as DataFrame
    """
    dirname = 'data'
    cities_list_file = "postesSynop.csv"
    column_names = ['numer_sta',
                    'date',
                    't',
                    'u',
                    'rr3']
    column_types = {
        'numer_sta':np.int32,
        'date':str,
        't':np.float32,
        'u':np.float32,
        'rr3':np.float32
    }

    path_here = os.path.dirname(__file__)
    path_to_data = os.path.join(path_here, dirname)
    files = [f for f in os.listdir(path_to_data) if os.path.isfile(os.path.join(path_to_data,f))]
    data = None
    for f in files:
        if f == cities_list_file or not f.endswith('.csv') or not f.startswith('synop'):
            pass
        else:
            try:
                print('[meteo.py] Loading weather data file {:s}'.format(f))
                complete_path = os.path.join(path_to_data, f)
                datatemp = pd.read_csv(complete_path,
                                       sep=';',
                                       header=0,
                                       usecols=column_names,
                                       dtype=column_types,
                                       na_values="mq")
                if data is None :
                    data = datatemp
                else :
                    data = pd.concat([data, datatemp])
            except Exception as e:
                print(e)

    #load list of stations
    print('[meteo.py] Loading weather stations data file {:s}'.format(cities_list_file))
    stations = {}
    with open(os.path.join(path_to_data, cities_list_file)) as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            d = {
                'numer_sta':int(row['ID']),
                'Nom':row['Nom'],
                'Altitude': float(row['Altitude']),
                'location': [float(row['Latitude']), float(row['Longitude'])]
            }
            stations[d['numer_sta']] = d

    return data, stations


def _clean_data():
    """ Cleans data (pandas DataFrame containing climate data

    :return:
    """

    #add datetime data
    data['datetime'] = data['date'].apply(lambda x: datetime.datetime.strptime(str(x), '%Y%m%d%H%M%S'))
    #set station number as index
    data.set_index('numer_sta', inplace=True)
    #convert to celsuis degrees
    data['t'] = data['t'].apply(lambda x: x-273.15)


def distance(loc1, loc2):
    """ Distance between two points represented by their [lat, long] coordinates
    :param loc1: [lat, long] in degrees
    :param loc2:
    :return: distance in km

    more info on http://en.wikipedia.org/wiki/Great-circle_distance
    """
    lat1 = math.radians(loc1[0])
    lat2 = math.radians(loc2[0])
    long1 = math.radians(loc1[1])
    long2 = math.radians(loc2[1])
    return 6371.0*math.acos(
        math.sin(lat1)*math.sin(lat2) + math.cos(lat1)*math.cos(lat2)*math.cos(math.fabs(long1-long2))
    )

def find_closest_station(location):
    """ Returns the closest station among the ones in 'stations'

    :param location: [lat, long] in degrees
    :return: (numer_sta, station_dict, dist)
     - station number (as index of data)
     - station as dict
     - distance in km
    """
    if not(type(location)==list and len(location)==2) :
        pass
    #measure distance between given location and all the meteo stations
    distances = [ (k, distance(location, v['location'])) for k, v in stations.items()]
    #sort by distance  and return the first one
    distances.sort(key=lambda x: x[1], reverse=False)
    code = distances[0][0]
    return code,  stations[code], distances[0][1]


def get_climate_data(insee_code, dates=None, date_start=None, date_end=None, freq='D'):
    """

    :param insee_code: insee code of the city to lookup
    :param dates: one datetime object or a list of
    :param date_start:
    :param date_end:
    :param freq:
    :return: dictionary with three keys: city_info, meteo_station, meteo_data
    {
       "city_info": {
          "Nom": "Paris",
          "code_postal": "75000",
          "surface": 105.63,
          "distance_to_station_km": 16.25557543115886,
          "location": [
             48.86080170979514,
             2.3457999087116095
          ],
          "Altitude": 60.0,
          "Insee": "75056",
          "pop99": 2125246
       },
       "meteo_station": {
          "Nom": "ORLY",
          "location": [
             48.716833,
             2.384333
          ],
          "Altitude": 89.0,
          "numer_sta": 7149
       },
       "meteo_data": {
          "datetime": #numpy array of datetime objects,
          "temperature_degreeC": #numpy array of floats,
          "humidity_percent": #numpy array of floats,
          "rain_3h_mm": #numpy array of floats

          #all these array should have the same number of elements
          #datetime is sorted from early to late
       }
    }
    """

    if not dates:
        dates = pd.date_range(start=date_start, end=date_end, freq=freq)
    else:
        if isinstance(dates, list):
            dates = pd.DatetimeIndex(dates)
        else :
            dates = pd.DatetimeIndex([dates])

    columns_to_interpolate = ('t', 'u', 'rr3')
    dates = pd.DataFrame(index=dates, columns=columns_to_interpolate)

    city_info = insee.get_city_data(insee_code)
    code, station, distance_km = find_closest_station(city_info['location'])
    subdata = data.loc[code]
    subdata = subdata.set_index('datetime', inplace=False)
    subdata = subdata.loc[:, columns_to_interpolate]

    interpolated = pd.concat([subdata, dates]).sort_index().interpolate(method='time')

    result = interpolated.loc[dates.index]
    result = result.drop_duplicates() #for some reason, using inplace=True creates a warning (SettingWithCopyWarning)

    d={}
    d['meteo_data'] = {
        'datetime': result.index.values,
        'temperature_degreeC': result['t'].values,
        'humidity_percent': result['u'].values,
        'rain_3h_mm': result['rr3'].values
    }
    city_info['distance_to_station_km'] = distance_km
    d['city_info'] = city_info

    d['meteo_station'] = station

    return d['meteo_data'], d['city_info'], d['meteo_station']


def default_serializer(x):
    if isinstance(x, np.ndarray):
        return repr(x) #[default_serializer(v) for v in x.tolist()]
    #if isinstance(x, np.datetime64):
    #    return "t"
    return x

data, stations = _load_data()
_clean_data()

if __name__ == "__main__":
    #d = get_climate_data('75056', dates=datetime.datetime(year=2013,month=3,day=12,hour=12,minute=24))
    d = get_climate_data('75056', dates=["20130120"])


