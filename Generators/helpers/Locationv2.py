import urllib3
import xml.etree.ElementTree
import pymongo

import time
import random

import os
import re


class Location(object):

    def __init__(self):

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
        self.pool = urllib3.PoolManager(1)

        # preset for OpenRouteService
        self.tag = lambda t, x: "{http://www.opengis.net/%s}%s" % (t, x)


    def time_converter(self, duration):

        # convert the duration string to list
        repl_s = lambda s: s.replace("S", "")
        repl_m = lambda m: m.replace("M", " ")
        repl_h = lambda h: h.replace("H", " ")

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

        lapsed_time = (f["H"] * 3600) + (f["M"] * 60) + (f["S"])

        # return the combined time
        return lapsed_time

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
                random.randint(1, 4)
            )
        ]

        # end point
        point_z = random.choice(area)

        point_y = "%20".join(self.generate_detours(
            [point_x,*detours,point_z]
        ))

        transport = "Car"

        u = self.ors_url(point_x, point_z, "", transport)    # point_y
        url = self.pool.urlopen(
            "GET", u
        ).data.decode('utf-8')

        self.enforce_limit(self.ors_limit)

        e = xml.etree.ElementTree.fromstring(url)

        points = []
        lapsed_time = None
        for element in e.getiterator(self.tag("xls", "RouteInstruction")):
            if element.get("duration") is not None:
                lapsed_time = self.time_converter(element.get("duration"))
            if lapsed_time is not None:
                for child in element.getiterator(
                    self.tag("xls", "RouteInstructionGeometry")
                ):
                    points.append((lapsed_time,
                        [i.text for i in child[0] if i.tag == self.tag("gml","pos")]
                    ))

        return points


    def generate_detours(self, coords):
        for coord in coords:
            lat, lon = coord

            u = self.gn_url(lat, lon)

            url = self.pool.urlopen(
                "GET", u
            ).data.decode('utf-8')

            self.enforce_limit(self.gn_limit)

            e = xml.etree.ElementTree.fromstring(url)

            points = []
            for point in e.getiterator("line"):
                points = points + [
                    x.replace(" ", ",") for x in i.text.split(",")
                ]

        return points
