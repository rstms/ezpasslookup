#!/usr/bin/env python3

import requests
import time
from bs4 import BeautifulSoup
import sys

from incapsula import IncapSession

URL = 'https://www.e-zpassny.com'

ERROR_UNKNOWN = 'ERROR-Unknown'
ERROR_NODATA = 'ERROR-No Violations Match'

TIMEOUT = 60
DELAY_INTERVAL = .1
STANDOFF_MULTIPLIER = 1.01
RETRY_COUNT = 64 

FIELDS = [
 'org.apache.struts.taglib.html.TOKEN',
 'formid',
 'transponderNumber'
]


def get_page(s, url):
    print('GET %s' % url)
    r = s.get(url)
    print('status=%d' % r.status_code)
    if r.status_code == 200:
        return r
    return None

def remove_parms(url):
    if '?' in url:
            url = url.split('?')[0]
    return url

def lambda_handler(event, context):

    url = event['url']
    violation_number = event['violation_number']
    license_plate = event['license_plate']

    r = None
    tries = 0
    start_time = time.time()
    standoff = DELAY_INTERVAL
    while (tries < RETRY_COUNT) and (time.time() - start_time < TIMEOUT):

        # wait longer before each retry
        tries += 1
        if tries > 1:
            standoff *= STANDOFF_MULTIPLIER
            print('Sleeping %.2f seconds...' % standoff)
            time.sleep(standoff)

        s = requests.Session() 
        #s = IncapSession()
        print('%d Session %s' % (tries, s))

        # get home page first
        r = get_page(s, url)
        if not r:
            continue

        #soup = BeautifulSoup(r.text, 'lxml')
        #print(soup.prettify())

        vurl = 'vector/violations/violationInquiry.do'
        #vurl = 'vector/violations/violationInquiry.do?locale=en_US&from=Home'
        #vurl = 'payviolation'

        r = get_page(s, '%s/%s' % (url, vurl))
        if not r:
            continue

        soup = BeautifulSoup(r.text, 'lxml')

        m = soup.find_all('meta')
        if False:
            print('meta: %s' % m)
            url2 = [c['content'].split(';')[1] for c in m if 'url=' in c['content']][0].split('=')[1]
            r = get_page(s, remove_parms(url2))
            if not r:
                continue
            soup = BeautifulSoup(r.text, 'lxml')

        f = soup.form
        inputs = f.find_all('input')

        form_data = {}
    
        for i in inputs:
            print('input: %s' % i['name'])
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

        #print('%s%s' % (url, action))
        #for k,v in form_data.items():
        #    print('%s: %s' % (k,v))
        
        post_url = '%s%s' % (url, remove_parms(action))

        print('POST %s' % post_url)
        #r = s.post(post_url, data=form_data)
        r = s.post(post_url, data=form_data, proxies={'https': 'localhost:8080'}, verify=False)
        print('status=%s' % r.status_code)

        if r.status_code == 200:
            break
        else:
            r = None

    if not r:
        print('Error: retries exhausted')
        return ERROR_UNKNOWN

    soup = BeautifulSoup(r.text, 'lxml')

    # find key table defs; these aren't marked well, so drill into the dom to find them
    try:
        ktds = soup.find_all('tbody')[1].tr.td.table.tr.td.table.tr.find_all('td')
    except IndexError:
        print('ERROR: tbody parse error: %s' % soup.prettify())
        return ERROR_UNKNOWN

    keys = []
    for td in ktds[1:]:
        #print('%s' % td.text.strip())
        keys.append(td.text.strip())

    #print('keys: %s' % repr(keys))
    expected_keys = ['Violation No.', 'License Plate', 'Date & Time', 'Facility', 'Status', 'Toll', 'Fee', 'Amt Due']
    if keys != expected_keys:
        print('Error: keys mismatch: keys=%s, expected=%s' % (keys, expected_keys))
        return ERROR_UNKNOWN

    # the value table defs are all marked with a unique class, so find them that way
    vtds = soup.form.find_all('td', attrs={'class': 'cl'})

    #print('ktds %d %s' % (len(ktds), ktds))
    #print('vtds %d %s' % (len(vtds), vtds))

    # multiple rows of vtds may exist.  we assume len(vtds) % len(ktds) == 0
    if len(vtds) % len(ktds):
        print('Error: parsing vtds=%s' % repr(vtds))
        return ERROR_UNKNOWN

    ret=[]
    for i in range(0, len(vtds), len(ktds)):
        row = {}
        j = i
        for key in keys:
            j+=1
            row[key] = vtds[j].text.strip()
        ret.append(row)
            
    return ret

if __name__ == '__main__':
    event={}
    event['violation_number'] = sys.argv[1]
    event['license_plate'] = sys.argv[2]
    event['url'] = URL
    ret = lambda_handler(event, None)
    print('%s' % ret)
    #import pdb; pdb.set_trace()
