#!/usr/bin/env python3

import requests
import time
from bs4 import BeautifulSoup
import sys

VIOLATION_NUMBER = 'T021775658460'
LICENSE_PLATE = 'FEB6625'

URL = 'https://www.e-zpassny.com'

TIMEOUT = 60
DELAY_INTERVAL = 1

FIELDS = [
 'org.apache.struts.taglib.html.TOKEN',
 'formid',
 'transponderNumber'
]

def fatal(msg):
    print('fatal: %s' % msg)
    sys.exit(-1)

def get_page(s, url):
    start_time = time.time()
    while time.time() - start_time < TIMEOUT:
        #print('GET %s' % url)
        r = s.get(url)
        #print('status=%d' % r.status_code)
        if r.status_code == 200:
            return r
        time.sleep(DELAY_INTERVAL)
    fatal('timeout error')

def scrape(url, violation_number, license_plate):
    s = requests.Session()
    r = get_page(s, '%s/%s' % (url, 'payviolation'))
    soup = BeautifulSoup(r.text, 'lxml')
    m = soup.find_all('meta')
    url2 = [c['content'].split(';')[1] for c in m if 'url=' in c['content']][0].split('=')[1]
    r = get_page(s, url2)
    soup = BeautifulSoup(r.text, 'lxml')

    f = soup.form
    inputs = f.find_all('input')

    form_data = {}
    
    for i in inputs:
        #print('input: %s' % i['name'])
        if i['name'] in FIELDS:
            form_data[i['name']] = i['value']

    form_data['violationNumber'] = violation_number
    form_data['licensePlate'] = license_plate
    form_data['licenseState'] = 'NY'
    form_data['licenseCountry'] = 'USA'
    form_data['btnSearch.x'] = 49
    form_data['btnSearch.y'] = 6

    for line in [l for l in soup.prettify().split('\n') if 'hidElement.' in l]:
        #print('element: %s' % line)
        if '"value"' in line:
            form_data['ctokenElem'] = line.split(',')[1].split("'")[1]

    action = f['action']
    if '?' in action:
        action = action.split('?')[0]

    #print('%s%s' % (url, action))
    #for k,v in form_data.items():
    #    print('%s: %s' % (k,v))
        
    post_url = '%s%s' % (url, action)

    #print('POST %s' % post_url)
    r = s.post(post_url, data=form_data)
    #print('status=%s' % r.status_code)

    soup = BeautifulSoup(r.text, 'lxml')

    ktds = soup.find_all('tbody')[1].tr.td.table.tr.td.table.tr.find_all('td')
    keys = []
    for td in ktds[1:]:
        #print('%s' % td.text.strip())
        keys.append(td.text.strip())


    vtds = soup.form.find_all('td', attrs={'class': 'cl'})

    print('[')
    i=0
    for td in vtds[1:]:
        if i==0:
            print('{')
        print('"%s":"%s"%s' % (keys[i], td.text.strip(), '' if i==len(keys)-1 else ','))
        i += 1
        if i >= len(keys):
            i=0
            print('}')
    print(']')

    #import pdb; pdb.set_trace()

if __name__ == '__main__':
    scrape(URL, VIOLATION_NUMBER, LICENSE_PLATE)
