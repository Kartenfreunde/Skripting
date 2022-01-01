import requests
from bs4 import BeautifulSoup

import urlsnapshot


GDP_URLS = ['https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-ost',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-nord',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-mitte',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-sued',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/a-ch-fl-suedtirol']

APLF_URL = 'http://www.aplf-planetariums.org/en/index.php?onglet=planetariums&menu=liste_country&filtre=GERMANY'
ZVSD_URL = 'http://www.zvsd.org/Verzeichnis-Planetarien-Sternwarten'
REDSHIFT_URL = 'https://www.redshift-live.com/ext/de/magazine/articles/Planetarien/13336-Verzeichnis_der_Planetarien-1'


def _gdp_html(url: str):
    return BeautifulSoup(requests.get(url).text, "html.parser").find("div", {"class": "content100"}).prettify()


def _redshift_html(url: str):
    return BeautifulSoup(requests.get(url).text, "html.parser").find("div", {"id": "magazine_article_detail_content"}).prettify()


if __name__ == '__main__':
    snapshots = {url: _gdp_html(url) for url in GDP_URLS}
    snapshots[APLF_URL] = requests.get(APLF_URL).text
    snapshots[ZVSD_URL] = requests.get(ZVSD_URL).text
    snapshots[REDSHIFT_URL] = _redshift_html(REDSHIFT_URL)
    urlsnapshot.publish_snapshots(snapshots)
