import requests
from bs4 import BeautifulSoup

import urlsnapshot


GDP_URLS = ['https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-ost',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-nord',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-mitte',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-sued',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/a-ch-fl-suedtirol']


def _gdp_html(url: str):
    return BeautifulSoup(requests.get(url).text, "html.parser").find("div", {"class": "content100"}).prettify()


if __name__ == '__main__':
    urlsnapshot.publish_snapshots({url: _gdp_html(url) for url in GDP_URLS})
