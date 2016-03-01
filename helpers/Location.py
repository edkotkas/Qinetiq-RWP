import json
import random
import urllib3                  # retrieve path xml
import xml.etree.ElementTree    # analyse path xml


X_GENERATING = "Generating..."
X_DONE = "Done"


class Location(object):

    def __init__(self):

        # postcode data
        self.data = None
        try:
            with open("helpers/info/postcodes.json") as postcodes:
                self.data = json.load(postcodes)
        except:
            raise Exception("Could not load postcodes.")

        # coordinates for England(only)
        self.area = [
            (float(i['longitude']), float(i['latitude'])) \
                     for i in self.data if i['country'] == 'ENG'
        ]

        # standard url formatting
        self.URL = \
            lambda start, end, via, transport: \
                "http://openls.geog.uni-heidelberg.de/route?"+\
                "start=%f,%f" % start+\
                "&end=%f,%f" % end+\
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
                "&instructions=false"

        try:
            with open("helpers/.pws", "r") as pws:
                un = pws.readline()
        except:
            raise Exception("Could not load UN data.")

        self.POI_URL = lambda lat, lng: \
            "http://api.geonames.org/findNearbyStreetsOSM?" + \
            "lat=%s" % lat + \
            "&lng=%s" % lng + \
            "&username=" + un.strip()

        # movement types
        self.transport = ['Car', 'Pedestrian', 'Bicycle', 'HeavyVehicle']

        # starting point
        self.start_point = None

        # ending point
        self.end_point = None

        # waypoints between
        self.waypoints = None

        self.tag = lambda x: "{http://www.opengis.net/gml}"+x

        self.pool = urllib3.PoolManager(1)

    def generate(self):
        """
        Generate whole traversal between points, within a real travel time.
        """
        print(X_GENERATING)

        # initialise location data
        self.generate_points()

        # starting point
        point_a = self.get_start()
        # ending point
        point_z = self.get_end()
        # via points
        waypoints = self.get_waypoints()

        # print(point_a, point_z, waypoints)

        # current transportation type
        current_transport = random.choice(self.transport)
        # print(current_transport)

        u = self.URL(point_a, point_z, waypoints, "Car")
        # print(u)

        url = self.pool.urlopen(
            "GET", u
        ).data.decode('utf-8')
        # path xml ElementTree
        e = xml.etree.ElementTree.fromstring(url)

        # path points
        path = []
        for i in e.getiterator():
            if i.tag == self.tag("pos"):
                lon, lat = i.text.split(" ")
                path.append("%s,%s" % (lon, lat))

        print(X_DONE)
        return path

    def _generate_pois(self, lat, lng):

        u = self.POI_URL(lat, lng)

        url = self.pool.urlopen(
            "GET", u
        ).data.decode('utf-8')

        # path xml ElementTree
        e = xml.etree.ElementTree.fromstring(url)

        pois = []
        for i in e.getiterator("line"):
            pois = pois + [x.replace(" ", ",") for x in i.text.split(",")]

        return pois

    def generate_points(self):
        # set start_point
        self.start_point = random.choice(self.area)
        # remove start_point, so end is not same
        self.area.remove(self.start_point)
        # set end_point
        self.end_point = random.choice(self.area)
        # remove end_point, so waypoints don't repeat
        self.area.remove(self.end_point)

        #set waypoints
        way_amount = random.randint(1, 2)
        way_points = [
            '%f,%f' % random.choice(self.area) for _ in range(way_amount)
        ]

        pois = []
        for points in [self.start_point, self.end_point] + way_points:
            p = self._generate_pois(points[1], points[0])
            for i in p:
                pois.append(i)

        way_points = way_points + pois
        self.waypoints = "%20".join(way_points)

    def get_waypoints(self):
        return self.waypoints

    def get_start(self):
        return self.start_point

    def get_end(self):
        return self.end_point


if __name__ == '__main__':
    l = PostCodes()
    l.generate()
