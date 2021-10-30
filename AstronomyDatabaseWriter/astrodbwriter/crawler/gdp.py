import re
from typing import List, Optional

import requests
import geocoder
from babel.numbers import parse_decimal
from bs4 import BeautifulSoup, Tag

from database import UNKNOWN
from database.planetarium import Planetarium, MobilityType, SeatArrangement, \
    OptomechanicalProjectorManufacturer, FulldomeSoftwareManufacturer

# currently, all places are saved in these four links
URLS = ['https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-ost',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-nord',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-mitte',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/d-sued',
        'https://www.gdp-planetarium.org/planetarien/liste-der-planetarien/a-ch-fl-suedtirol']


def retrieve_data() -> List[Planetarium]:
    planetariums = []
    failures = 0
    for url in URLS:
        planetariums_html: List[Tag] = BeautifulSoup(requests.get(url).text, "html.parser")\
            .find_all("div", {"class": "planetarium-wrapper"})
        for html in planetariums_html:
            location = _get_location(html)
            try:
                address = _get_address(html)
                coords = geocoder.osm(address)
                planetariums.append(Planetarium(institution="Planetarium",  # dummy - read from wiki
                                                location=location,
                                                address=address,
                                                country_code=_get_country_code(html),
                                                latitude=coords.latlng[0],
                                                longitude=coords.latlng[1],
                                                website=_get_website(html),
                                                dome_diameter=_get_dome_diameter(html),
                                                dome_tilt=_get_dome_tilt(html),
                                                mobility=_get_mobility_type(html),
                                                seats=_get_seats(html),
                                                seat_arrangement=_get_arrangement(html),
                                                optomechanical_projector=_get_optomechanical_projector(html),
                                                optomechanical_projector_manufacturer=_get_optomechanical_projector_manufacturer(html),
                                                fulldome_software=_get_fulldome_software(html),
                                                fulldome_software_manufacturer=_get_fulldome_software_manufacturer(html),
                                                opening_year=_get_opening_year(html),
                                                visitors_per_year=UNKNOWN  # read from wiki
                                                ))
            except Exception as e:
                print("Failed to process " + location + ": " + str(e))
                failures += 1
    print(str(failures) + " failures")
    return planetariums


def _get_location(html: Tag) -> str:
    # contents[0] is the newline before the heading tag, so we need the text from contents[1]
    # the heading ends with " (MOBIL)" if it is a mobile planetarium, but we don't want to have
    # this in the location here
    # we apply a strip() here just for sure
    return _get_left_column(html).find("h3").get_text().removesuffix(" (MOBIL)").strip()


def _get_mobility_type(html: Tag) -> MobilityType:
    # contents[0] is the newline before the heading tag, so we need the text from contents[1]
    # the heading ends with " (MOBIL)" if it is a mobile planetarium
    return \
        MobilityType.MOBILE if _get_left_column(html).find("h3").get_text().endswith(" (MOBIL)") \
        else MobilityType.STATIONARY


def _get_address(html: Tag) -> str:
    # first, get all lines from the first paragraph except the first one (which always contains the
    # (beginning of) the planetarium's name
    lines = [line.strip()
             for line in _get_left_column(html).find("p").contents if isinstance(line, str)]
    lines.pop(0)
    # the last line is always like "D-04838 Eilenburg"
    zip_and_location = lines.pop()
    # remove country prefix
    zip_and_location = zip_and_location[zip_and_location.find("-")+1:]
    return _get_first_part_of_address(lines) + ", " + zip_and_location


def _get_first_part_of_address(candidates: List[str]) -> str:
    # we have to find out which line contains the first part of the address
    # first of all, check for additional addresses marked with "Postadresse" - we don't want these
    # (except if there is no other address given); we do the check right at the beginning (to avoid
    # that the marker is cut off in the next step) and remember the result for later
    mailing_address = ["postadresse" in cand.lower() for cand in candidates]
    # sometimes, an additional information in brackets is appended, so remove that first if present
    candidates = [cand[:cand.rfind("(")].strip() if "(" in cand else cand for cand in candidates]
    # well, if we only have one line left, it's easy
    if len(candidates) == 1:
        return candidates[0]
    # check lines against regex with typical address structure (i. e. ending with a number which is
    # optionally followed by a single letter)
    matching_candidates = [cand for cand in candidates if re.search(".*[0-9] ?[a-zA-Z]?$", cand)]
    if len(matching_candidates) == 1:
        return matching_candidates[0]
    elif len(matching_candidates) > 0:
        # if we could at least reduce the number of candidates, we continue working with the reduced
        # list
        candidates = matching_candidates
    # remove candidates which are marked as mailing address
    candidates = [cand for idx, cand in enumerate(candidates) if not mailing_address[idx]]
    # return the last candidate (because the address is usually at the bottom of the paragraph)
    return candidates[-1]


def _get_country_code(html: Tag) -> str:
    # we take the zip code line (which is the last line in the address paragraph)
    address_paragraph = _get_left_column(html).find("p").contents
    zip_and_location = [line.strip() for line in address_paragraph if isinstance(line, str)][-1]
    country = zip_and_location[:zip_and_location.find("-")]
    if country == "A":
        return "AT"
    elif country == "CH":
        return "CH"
    elif country == "D":
        return "DE"
    elif country == "FL":
        return "LI"
    elif country == "I":
        return "IT"
    raise ValueError("Unknown country code: " + country)


def _get_website(html: Tag) -> Optional[str]:
    # the contact paragraph is the last one in the left column and it has to contain an <a> tag
    url_tag = _get_left_column(html).find_all("p")[-1].find("a")
    if url_tag is None:
        return None
    url: str = url_tag["href"]
    # for consistent formatting, ensure that the URL starts with "www" and remove any protocol info
    url = url.removeprefix("http://")
    url = url.removeprefix("https://")
    if not url.startswith("www."):
        url = "www." + url
    # also remove any path information
    if "/" in url:
        url = url[:url.find("/")]
    return url


def _get_dome_diameter(html: Tag) -> float:
    first_line = _get_right_column(html).find("p").contents[0]
    return parse_decimal(first_line.split()[0], "de")


def _get_dome_tilt(html: Tag) -> float:
    first_line: str = _get_right_column(html).find("p").contents[0]
    tilt_strings = re.findall("[0-9]+ ?°", first_line)
    if len(tilt_strings) == 0:
        return 0.0
    # otherwise, we take the first matching string, remove "°" and the optional blank and parse it
    return float(tilt_strings[0][:-1].strip())


def _get_seats(html: Tag) -> Optional[int]:
    seat_line: str = _get_right_column(html).find("p").contents[2]
    # sometimes there are texts like "20-30", so we filter out all integers and take the biggest
    # return None if no integer is found (i. e. information is missing)
    return max([int(s) for s in re.findall(r"\b\d+\b", seat_line)])


def _get_arrangement(html: Tag) -> SeatArrangement:
    seat_line: str = _get_right_column(html).find("p").contents[2]
    if "unidirektional" in seat_line.lower():
        return SeatArrangement.UNIDIRECTIONAL
    if "konzentrisch" in seat_line.lower() or "epizentrisch" in seat_line.lower():
        return SeatArrangement.CONCENTRIC
    if "variabel" in seat_line.lower():
        return SeatArrangement.VARIABLE
    raise ValueError("No known arrangement type found in " + seat_line)


def _get_opening_year(html: Tag) -> int:
    return int(_get_right_column(html).find("p").contents[-1])


def _get_optomechanical_projector(html: Tag) -> Optional[str]:
    projector = _get_right_column(html).find("p").contents[-9].strip()
    if projector == "-":
        return None
    return projector


def _get_optomechanical_projector_manufacturer(html: Tag)\
        -> Optional[OptomechanicalProjectorManufacturer]:
    projector = _get_optomechanical_projector(html)
    if projector is None:
        return None
    projector = projector.lower()
    if "eigenbau" in projector or "selbstbau" in projector:
        return OptomechanicalProjectorManufacturer.SELF_MADE
    for manufacturer in OptomechanicalProjectorManufacturer:
        if str(manufacturer).lower() in projector:
            return manufacturer
    raise ValueError("Unknown manufacturer: " + projector)


def _get_fulldome_software(html: Tag) -> Optional[str]:
    software = _get_right_column(html).find("p").contents[-5].strip()
    if software == "-":
        return None
    return software


def _get_fulldome_software_manufacturer(html: Tag) \
        -> Optional[FulldomeSoftwareManufacturer]:
    software = _get_fulldome_software(html)
    if software is None:
        return None
    software = software.lower()
    if "eigenbau" in software or "selbstbau" in software:
        return FulldomeSoftwareManufacturer.SELF_MADE
    if "e&s" in software:
        return FulldomeSoftwareManufacturer.E_AND_S
    for manufacturer in FulldomeSoftwareManufacturer:
        if str(manufacturer).lower() in software:
            return manufacturer
    raise ValueError("Unknown manufacturer: " + software)


def _get_left_column(html: Tag) -> Tag:
    return html.find("div", {"class": "planetarium-adress"})


def _get_right_column(html: Tag) -> Tag:
    return html.find("div", {"class": "planetarium-technology"})
