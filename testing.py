__author__ = 'BenjaminHabert'


import json
import datetime
import numpy as np
#from Territoire.insee import insee
#print(json.dumps(insee.get_city_data(75056),indent=3))

from Territoire import meteo
from Territoire import insee
import pandas as pd
import matplotlib.pyplot as plt


print('*'*30)
print('Getting city information for insee code: 75056 (Paris)')
print('Call: {:s}'.format("insee.get_city_data('75056')"))
print(json.dumps(insee.get_city_data('75056'), indent=3))

print('*'*30)
print('Getting weather data for insee code: 75056 (Paris)')
print('Call: {:s}'.format('meteo.get_climate_data("75056", dates=["20130101", "20130102"])'))
meteo_data, city_infos, meteo_station = meteo.get_climate_data('75056', dates=["20130101", "20130102"])
print(json.dumps(meteo_data, indent=3, default=meteo.default_serializer))
print(json.dumps(city_infos, indent=3, default=meteo.default_serializer))
print(json.dumps(meteo_station, indent=3, default=meteo.default_serializer))

print('*'*30)
print('Getting weather in a range of dates for insee code: 75056 (Paris)')
print('Call: {:s}'.format("meteo.get_climate_data('75056',date_start='2013-01-01 12:30', date_end='2013-01-30 12:30',freq='H')"))
meteo_data, _, _ = meteo.get_climate_data('75056',date_start='2013-01-01 12:30', date_end='2013-01-15 12:30',freq='H')
plt.figure()
plt.plot(meteo_data['datetime'], meteo_data['temperature_degreeC'])
plt.show()



