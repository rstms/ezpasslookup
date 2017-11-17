#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import os
import time
import sys
import json

URL = 'https://www.e-zpassny.com'

ERROR_UNKNOWN = 'ERROR-Unknown'
ERROR_NODATA = 'ERROR-No Violations Match'

TOTAL_KEY = 'Total No of Violations:'
INFO_KEY = 'Violation Information'
ERROR_KEY = 'No violations match the information you entered.'

KEYS = ['Violation No.', 'License Plate', 'Date & Time', 'Facility', 'Status', 'Toll', 'Fee', 'Amt Due']

def handler(event, context):

    url = event.get('url') or URL
    violation_number = event.get('violation_number')
    license_plate = event.get('license_plate')

    try:
        os.mkdir('/tmp/data-path')
    except FileExistsError:
        pass

    try:
        os.mkdir('/tmp/cache-dir')
    except FileExistsError:
        pass

    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--homedir=/tmp')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--data-path=/tmp/data-path')
    chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')

    chrome_options.binary_location = 'headless-chrome/headless_shell'

    driver = webdriver.Chrome(
        executable_path='headless-chrome/chromedriver',
        chrome_options = chrome_options
    )

    vurl = 'vector/violations/violationInquiry.do'
    driver.get('%s/%s' % (url, vurl))

    if not 'E-ZPass' in driver.title:
        driver.close()
        return ERROR_UNKNOWN

    e = driver.find_element_by_name('violationNumber')
    e.clear()
    e.send_keys(violation_number)

    e = driver.find_element_by_name('licensePlate')
    e.clear()
    e.send_keys(license_plate)

    driver.find_element_by_name('btnSearch').click()

    if ERROR_KEY in driver.page_source:
        driver.close()
        return ERROR_NODATA

    # find number of violations
    items = []
    while True:

        if not TOTAL_KEY in driver.page_source:
            ret = ERROR_UNKNOWN
            break

        trows = [e.text for e in driver.find_elements_by_class_name('fd')]

        if not TOTAL_KEY in trows:
            ret = ERROR_UNKNOWN
            break

        tindex = trows.index(TOTAL_KEY)
        total = int(trows[tindex+1])

        if not trows[tindex+2].startswith(INFO_KEY):
            ret = ERROR_UNKNOWN
            break
        
        rows = trows[tindex+2].split('\n')

        #for i in range(len(rows)):
        #    print('%d %s' % (i, repr(rows[i])))

        cnums = rows[0].split()

        if cnums[2] == '1' and cnums[3] == 'item':
            snum = 1
            enum = 1
            if total != 1:
                ret = ERROR_UNKNOWN
                break
        else:
            snum = int(cnums[2])
            enum = int(cnums[4])
            if total != int(cnums[6]):
                ret = ERROR_UNKNOWN
                break

        if snum != len(items) + 1:
            ret = ERROR_UNKNOWN
            break
    
        count = (enum - snum) + 1
        for i in range(0, count):
            item = {}
            for j in range(0, 8):
                item[KEYS[j]] = rows[2 + i * 8 + j].strip()
            items.append(item)

        if len(items) < total:
            driver.find_element_by_xpath("//a[@title='Goto next page']").click()
        else:    
            ret = items
            break

    driver.close()
    return ret

if __name__ == '__main__':
    event={}
    event['violation_number'] = sys.argv[1]
    event['license_plate'] = sys.argv[2]
    event['url'] = URL
    ret = handler(event, None)
    print('%s' % json.dumps(ret, sort_keys=True))
