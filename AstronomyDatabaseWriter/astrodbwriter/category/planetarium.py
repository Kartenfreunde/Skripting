from dataclasses import dataclass
from enum import Enum, unique
from typing import Optional, Union

from util import Unknown


@unique
class MobilityType(Enum):
    MOBILE = "mobile"
    STATIONARY = "stationary"

    def __str__(self):
        return self.value


@unique
class SeatArrangement(Enum):
    CONCENTRIC = "concentric"
    UNIDIRECTIONAL = "unidirectional"
    VARIABLE = "variable"

    def __str__(self):
        return self.value


@unique
class OptomechanicalProjectorManufacturer(Enum):
    RSA_COSMOS = "RSA Cosmos"
    GOTO = "GOTO"
    SELF_MADE = "self-made"
    ZEISS = "Zeiss"
    BERGER = "Astrogeräte Berger"

    def __str__(self):
        return self.value


@unique
class FulldomeSoftwareManufacturer(Enum):
    DIGITALIS_EDUCATION = "Digitalis Education"
    E_AND_S = "Evans & Sutherland"
    RSA_COSMOS = "RSA Cosmos"
    SELF_MADE = "self-made"
    SKY_SKAN = "Sky-Skan"
    VIOSO = "Vioso"
    ZEISS = "Zeiss"

    def __str__(self):
        return self.value


@dataclass(frozen=True)
class Planetarium:

    name:               str
    location:           str
    address:            Optional[str]
    country_code:       str  # ISO 3166 two-letter code
    latitude:           float  # degree
    longitude:          float  # degree
    website:            Optional[str]
    dome_diameter:      float  # meters
    dome_tilt:          float  # degree
    mobility:           MobilityType
    seats:              int
    seat_arrangement:   SeatArrangement
    opening_year:       int
    visitors_per_year:  Union[Unknown, int]

    optomechanical_projector:               Optional[str]
    optomechanical_projector_manufacturer:  Optional[OptomechanicalProjectorManufacturer]
    fulldome_software:                      Optional[str]
    fulldome_software_manufacturer:         Optional[FulldomeSoftwareManufacturer]

    def __eq__(self, other):
        return isinstance(other, Planetarium)\
               and self.name == other.name\
               and self.location == other.location

    def __hash__(self):
        return hash((self.name, self.location))
