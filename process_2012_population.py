__author__ = 'benjaminhabert'

import os
import re

pattern_city = re.compile(r'<http://id\.insee\.fr/demo/populationLegale/(\w+)/(\d+)/')
pattern_population = re.compile(r'idemo:populationTotale\s+"(\d+)"')


print(os.listdir('./'))
current_city = -1
with open('popleg-2012.ttl') as f:
    for i, line in enumerate(f):
        if i>100:
            break
        line = line.strip()
        result_city = re.match(pattern_city, line)
        result_pop = re.match(pattern_population,line)
        if result_city:
            print('FOUNT CITY',result_city.group(1), int(result_city.group(2)))
        elif result_pop:
            print('FOUNT POP', int(result_pop.group(1)))
        print(line)

