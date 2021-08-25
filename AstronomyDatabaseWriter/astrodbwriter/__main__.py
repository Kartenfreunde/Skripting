from category.planetarium import *
import util

# Entry point for the astronomy database writer.
# To be continued...

if __name__ == '__main__':
    print("Hello World! This is the astronomy database writer.")

    pl = Planetarium(name="Testplanetarium",
                     location="Musterstadt",
                     address="Bahnhofstraße 1, 12345 Musterstadt",
                     country_code="DE",
                     latitude=50,
                     longitude=10,
                     website=None,
                     dome_diameter=10,
                     dome_tilt=0,
                     mobility=MobilityType.STATIONARY,
                     seats=100,
                     seat_arrangement=SeatArrangement.CONCENTRIC,
                     optomechanical_projector="Zeiss Universarum IX",
                     optomechanical_projector_manufacturer=OptomechanicalProjectorManufacturer.ZEISS,
                     fulldome_software=None,
                     fulldome_software_manufacturer=None,
                     opening_year=2000,
                     visitors_per_year=util.UNKNOWN)

    util.write_csv("planetariums.csv", [pl])
