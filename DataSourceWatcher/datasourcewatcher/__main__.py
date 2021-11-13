import requests
import urlcheck


URLS = ['https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-ost',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-nord',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-mitte',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-sued',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/a-ch-fl-suedtirol']


if __name__ == '__main__':
    urlcheck.publish_snapshots({url: requests.get(url).text for url in URLS})
