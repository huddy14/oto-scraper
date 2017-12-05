#!/bin/python3

from bs4 import BeautifulSoup as soup
import requests
import re
import sys

# todo: rewirte to use lambda
# todo: refactor so more search parameters will be available
# todo: mobile to class? or pretty print the result
# data range 
# connect to db
# use opt instead of argv

def filter_by_mark(name, mobiles):
    filtered = []

    for mobile in mobiles:
        if name.lower() not in mobile['model'].lower():
            continue
        filtered.append(mobile)

    return filtered

PRICE_MIN = 1000 if len(sys.argv) < 3 else sys.argv[2]
PRICE_MAX = 3000 if len(sys.argv) < 4 else sys.argv[3]

req = requests.get('https://www.otomoto.pl/osobowe/gliwice/?search%5Bfilter_float_price%3Afrom%5D={0}&search%5Bfilter_float_price%3Ato%5D={1}&search%5Bfilter_float_engine_power%3Afrom%5D=80&search%5Bfilter_enum_fuel_type%5D%5B0%5D=petrol&search%5Bfilter_enum_gearbox%5D%5B0%5D=manual&search%5Bfilter_enum_transmission%5D%5B0%5D=front-wheel&search%5Bbrand_program_id%5D%5B0%5D=&search%5Bdist%5D=300&search%5Bcountry%5D='.format(PRICE_MIN, PRICE_MAX))

html_to_parse = req.text

parser = soup(html_to_parse, 'html.parser')

list_container = parser.findAll('div', {'class' : ['offers', 'list']})

assert len(list_container) == 1

offers = list_container[0].findAll('article', {'class' : ['offer-item', 'is-row']})

mobiles = []

for offer in offers:
    mobile = {}
    
    # getting model and link
    model_link  = offer.find('a', {'class' : 'offer-title__link'})

    # getting only id from {ad_id : "234324"}
    ninja_id = model_link['data-ninja-extradata']
    mobile['id'] = re.findall('\d+', ninja_id)[0]

    mobile['link'] = model_link['href']
    mobile['model'] = model_link.text.strip()


    # getting price
    price = offer.find('span', {'class' : 'offer-price__number'})
    mobile['price'] = int(price.find(text=True).strip().replace(' ',''))

    # getting properties
    params = offer.find('ul', {'class' : 'offer-item__params'})

    properties = []
    for param in params.findAll('span'):
        properties.append(param.text.strip())

    mobile['properties'] = properties

    # getting location
    location = offer.find('span', {'class' : 'offer-item__location'})
    # we strip any html tags from there
    mobile['location'] = ' '.join(location.get_text().strip().split())

    mobiles.append(mobile)

search_model = sys.argv[1]

if search_model:
    print(filter_by_mark(search_model, mobiles))

