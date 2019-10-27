import re
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://minfin.com.ua/currency/'

num_round = lambda num: round(num, 5)

r = requests.get(BASE_URL)
soap = BeautifulSoup(r.text, 'lxml')
hpar = soap.select('span.mfcur-nbu-full-wrap')
parsed_hpar = []
for msn in hpar:
    txt = msn.get_text()
    parsed_hpar.append(txt)

pattern = r'\d\d.\d+'
rub_pattern = r'\d.\d+'
exchange_rate = {
        'USD': float(re.search(pattern, parsed_hpar[0])[0]),
        'EUR': float(re.search(pattern, parsed_hpar[1])[0]),
        'RUB': float(re.search(rub_pattern, parsed_hpar[2])[0])
    }
