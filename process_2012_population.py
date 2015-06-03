# coding: utf8
#from __future__ import unicode_literals
__author__ = 'benjaminhabert'


import re
import csv


def parse_2012_pop():
    """ parse file 'popleg-2012.ttl'
        create file 'pop2012-communes.csv'

    :return: none
    """
    pattern_city = re.compile(r'<http://id\.insee\.fr/demo/populationLegale/(\w+)/([\dA-Z]+)/')
    pattern_population = re.compile(r'idemo:populationTotale\s+"(\d+)"')
    current_city = -1
    n_city = 0
    with open('popleg-2012.ttl') as f:
        f_out = open('pop2012_communes.csv','w')
        f_out.write('insee,pop2012\n')
        for i, line in enumerate(f):
            if i>300:
                pass
            line = line.strip()
            result_city = re.match(pattern_city, line)
            result_pop = re.match(pattern_population,line)
            if result_city:
                #print('FOUNT CITY',result_city.group(1), int(result_city.group(2)))
                if result_city.group(1) == 'commune' :
                    current_city = result_city.group(2)
                else :
                    current_city = -1
            elif result_pop:
                #print('FOUNT POP', int(result_pop.group(1)))
                if current_city != -1 :
                    n_city += 1
                    print('{:5d}  CITY: {:s} \t POP: {:d}'.format(n_city,current_city, int(result_pop.group(1))))
                    f_out.write('{:s},{:d}\n'.format(current_city, int(result_pop.group(1))))
        f_out.close()


def add_2012_pop():
    """ merge files 'pop2012-communes.csv' and 'Codes-INSEE-communes-geolocalisees.csv'

    :return:
    """
    geofile = 'Territoire/data/Codes-INSEE-communes-geolocalisees.csv'
    insee_data = {}
    with open(geofile) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            code = ''
            try:
                code = '{:5d}'.format(int(row['Insee']))
            except Exception:
                code = row['Insee']
            if code:

                #row["Nom"] = row["Nom"].decode('latin1')
                insee_data[code] = row


    popfile = 'pop2012_communes.csv'
    pop_data = {}
    with open(popfile) as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            code = ''
            try:
                code = '{:5d}'.format(int(row['insee']))
            except Exception:
                code = row['insee']
            if code:
                pop_data[code] = row


    print(len(insee_data), len(pop_data))
    for insee in insee_data.keys():
        if insee in pop_data:
            insee_data[insee]['pop2012'] = pop_data[insee]['pop2012']
        else :
            # il y a une 20 aine de cas ...
            insee_data[insee]['pop2012'] = insee_data[insee]['pop99']


    columns = ['Insee','Nom','Altitude','code_postal','longitude_radian','latitude_radian','pop99','pop2012','surface']
    example = insee_data[insee_data.keys()[0]]
    mergefile = 'Territoire/data/INSEE_communes.csv'
    with open(mergefile,'w') as f:
        writer = csv.DictWriter(f, fieldnames=columns,lineterminator='\n')
        writer.writeheader()
        ks = insee_data.keys()
        ks.sort()
        for k in ks:
            writer.writerow(insee_data[k])


if __name__ == '__main__':
    # parse_2012_pop()
    add_2012_pop()
