# Territoire_API
This Python API provides climate and census data for cities in France.

## Data sources:
The project uses two data sources. One is the list of 36.000 cities in France, the other is weather data from
60 weather stations in France.

### List of cities
This list is handled by insee.py. The datafile is Codes-INSEE-communes-geolocalisees.csv The file can be accessed on
the opendata website:

https://www.data.gouv.fr/fr/datasets/geofla-communes/

The file contains the following information for 36.000 cities:
- insee code
- name of city
- population (census from year 1999)
- position (latitude and longitude)
- altitude
- city surface area in square km

### Weather Data
Access to weather data is done with meteo.py. The datafiles are :
 - postesSynop.csv: A list of 60 weather stations in France. More specifically, the file contains:
    - weather station code
    - station name
    - position (latitude and longitude)
    - altitude
 - several files labeled synop.YYYYMM.csv. Each of this files contains weather data for all the weather station for
   a given year and month. There is a lot a measured data in this file, but the API only retrieves the following for now:
    - weather station code
    - time of measurement (every three hour)
    - temperature (Kelvin in the datafile)
    - humidity percentage
    - amount rained in the last three hours (mm)

This data can be found here:

https://www.data.gouv.fr/fr/datasets/donnees-d-observation-des-principales-stations-meteorologiques/

https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=90&id_rubrique=32

At the moment, the data folder only contains the weather data from file 'synop.201301.csv'. Other data files can be
downloaded on the previous website and added to the data folder.

## Usage
Their is no pip installation at the moment. The project is at an early stage. Here is what I recommand:
- download and unzip the folder from git.
- place the Territoire folder where you are working.
- download weather data for the period you want from donneespubliques.meteofrance.fr; add these csv files to the
  Territoire/data folder.

Then you are ready to use the API. Here are a few basic calls.

    from Territoire import insee
    from Territoire import meteo

### Getting city information

    insee.get_city_data('75056')
    
the only parameter for this function is the insee code of the city.
returns:

```python
{
   "location": [
      48.86080170979514,
      2.3457999087116095
   ],
   "Nom": "Paris",
   "surface": 105.63,
   "Altitude": 60.0,
   "Insee": "75056",
   "pop99": 2125246,
   "code_postal": "75000"
}
```

### Getting weather data
You can request weather for a city using the insee code of that city. The file meteo.py will find the position of
the city you are looking for (through insee.py) and find the closest weather station among its list of 60 stations.
The weather you receive is the one of the weather station, not the one of the city you are querying.

    weather_data, city_infos, weather_station = meteo.get_climate_data("75056", dates=["20130101", "20130102"])

Parameters:
 - first positional parameters is the insee code
 - period can be specified in two ways with names parameters:
    - one parameter: dates=[ a list of dates ]
    - three parameters:
       - date_start = date
       - date_end = date
       - freq = 'D'
   In each of these situations, date can be either a datetime object or or string that can be converted to a date.
   Examples of strings:
      '20130101'   -1rst of january
      '2013010112' -at none
      '2013-01-01 12:30'
   See the documentation of pandas.date_range() for more information

Returns:

weather_data: a dictionary contaiing several list. One of them is a list of datetimes and the others are measurements
for these times.
```python
{
   "humidity_percent": "array([ 90.,  92.])",
   "datetime": "array(['2013-01-01T01:00:00.000000000+0100',\n       '2013-01-02T01:00:00.000000000+0100'], dtype='datetime64[ns]')",
   "rain_3h_mm": "array([ 2.,  0.])",
   "temperature_degreeC": "array([ 7.6       ,  2.39998779])"
}
```
city_infos: infos from insee.py about the city you are querying. It also provides you with the distance from the
queried city and the closest meteo station found in the list
```python
{
   "location": [
      48.86080170979514,
      2.3457999087116095
   ],
   "Nom": "Paris",
   "distance_to_station_km": 16.25557543115886,
   "surface": 105.63,
   "Altitude": 60.0,
   "Insee": "75056",
   "pop99": 2125246,
   "code_postal": "75000"
}
```

weather_station. Informations about the closest weather station found
```python
{
   "location": [
      48.716833,
      2.384333
   ],
   "numer_sta": 7149,
   "Altitude": 89.0,
   "Nom": "ORLY"
}
```

## Dependencies
The project was done with Python 3.4
Libraries used:
 - pandas
 - numpy
 - core libraries
