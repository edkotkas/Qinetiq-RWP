import urllib3
import xml.etree.ElementTree
import datetime

import time
import random

import os
import re


class Location(object):

    def __init__(self):

        self.year = 2016
        self.month = 1
        self.day = 1
        self.hour = 10
        self.minute = 0
        self.second = 0
        self.current_time = datetime.datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second
        )

        # overhead blockers
        self.ors_limit = 1000   # 1000/h OpenRouteService
        self.gn_limit = 2000    # 2000/h GeoNames

        # import postcode data
        self.postcode_data = xml.etree.ElementTree.parse(
            "Generators/helpers/info/postcodes.xml"
        ).getroot()

        # OpenRouteService URL
        self.ors_url = \
            lambda start_coord, end_coord, via, transport: \
                "http://openls.geog.uni-heidelberg.de/route?"+\
                "start=%f,%f" % start_coord+\
                "&end=%f,%f" % end_coord+\
                "&via=%s" % via+\
                "&lang=en"+\
                "&distunit=MI"+\
                "&routepref=%s" % transport+\
                "&weighting=Recommended"+\
                "&avoidAreas="+\
                "&useTMC=false"+\
                "&noMotorways=false"+\
                "&noTollways=false"+\
                "&noUnpavedroads=false"+\
                "&noSteps=false"+\
                "&noFerries=false"+\
                "&instructions=true"

        # import private data
        try:
            with open("Generators/helpers/.pws", "r") as pws:
                UN = pws.readline()
        except:
            raise Exception("Could not load UN data.")

        # GeoNames URL
        self.gn_url = lambda lat, lng: \
            "http://api.geonames.org/findNearbyStreetsOSM?" + \
            "lat=%f" % lat + \
            "&lng=%f" % lng + \
            "&username=" + UN.strip()

        # default movement types
        self.transport = ['Car', 'Pedestrian', 'Bicycle', 'HeavyVehicle']

        # urllib manager
        self.pool = urllib3.PoolManager(2)

        # preset for OpenRouteService
        self.tag = lambda t, x: "{http://www.opengis.net/%s}%s" % (t, x)

        # time configuration
        self.year = 2016
        self.month = 1
        self.day = 1
        self.hour = 10
        self.minute = 0
        self.second = 0

        self.current_time = None

    def time_adder(self, duration):
        self.second += duration["S"]
        self.minute += duration["M"]
        self.hour += duration["H"]

        while self.second >= 60:
            self.second -= 60
            self.minute += 1
        while self.minute >= 60:
            self.minute -= 60
            self.hour += 1
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1
        while self.day >= 28:
            self.day -= 28
            if self.day == 0:
                self.day += 1
            self.month += 1
        while self.month >= 12:
            self.month -= 12
            if self.month == 0:
                self.mont += 1
            self.year += 1

        datetime.datetime
        self.current_time = datetime.datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second
        )

        return self.current_time

    def time_converter(self, duration):
        f = {
            "H": 0,
            "M": 0,
            "S": 0
        }
        lapsed_time = duration.replace("PT", "")

        if "H" in lapsed_time:
            lt = lapsed_time.split("H")
            h = int(lt[0])
            f["H"] = (h)
            lapsed_time = lt[1]
        if "M" in lapsed_time:
            lt = lapsed_time.split("M")
            m = int(lt[0])
            f["M"] = (m)
            lapsed_time = lt[1]
        if "S" in lapsed_time:
            lt = lapsed_time.split("S")
            s = int(lt[0])
            f["S"] = (s)

        # return the combined time
        return f

    def enforce_limit(self, service_limit):
        if service_limit <= 100:
            print("REACHED LIMIT, WAITING (1 hour) ...")
            time.sleep(3600)
            self.ors_limit = 1000
            self.gn_limit = 2000
        service_limit -= 1

    def generate(self):
        area = [
            coord.text.split("\t") \
                for coord in self.postcode_data.getiterator("coordinates")
        ]
        # swap coords for OpenRouteService suitability
        area = [
            (float(lat), float(lon)) for lon, lat in area
        ]

        # starting point
        point_x = random.choice(area)

        # detours
        detours = [
            random.choice(area) for _ in range(
                random.randint(0, random.randint(1, 4))
            )
        ]

        # end point
        point_z = random.choice(area)

        points_of_interest = [
            i for i in self.generate_detours([point_x,*detours,point_z])
        ]
        point_y = "%20".join([
            random.choice(points_of_interest) for _ in range(
                random.randint(1, int(len(points_of_interest)/2))
            )
        ])

        transport = "Car"

        u = self.ors_url(point_x, point_z, point_y, transport)
        url = self.pool.urlopen(
            "GET", u
        ).data.decode('utf-8')

        self.enforce_limit(self.ors_limit)

        e = xml.etree.ElementTree.fromstring(url)

        points = []
        lapsed_time = []
        for element in e.getiterator(self.tag("xls", "RouteInstruction")):
            if element.get("duration") is not None:
                lapsed_time.append(self.time_converter(element.get("duration")))
            if lapsed_time is not None:
                for child in element.getiterator(
                    self.tag("xls", "RouteInstructionGeometry")
                ):
                    points.append([
                        i.text for i in child[0] \
                            if i.tag == self.tag("gml","pos")
                    ])

        if len(lapsed_time) == 0 or len(points) == 0:
            # TODO: fix empty error
            return self.generate()
        else:
            result = []
            for index in range(len(points)):
                p = points[index]
                l = self.time_adder(lapsed_time[index])

                for dot in p:
                    result.append((l, dot))

            return result

    def generate_detours(self, coords):
        for coord in coords:
            lat, lon = coord

            u = self.gn_url(lon, lat)

            url = self.pool.urlopen(
                "GET", u
            ).data.decode('utf-8')

            self.enforce_limit(self.gn_limit)

            e = xml.etree.ElementTree.fromstring(url)

            for point in e.getiterator("line"):
                for x in point.text.split(","):
                    yield x.replace(" ", ",")

if __name__ == '__main__':
    l = Location()
    l.generate()
