from tkinter import *           # UI
import urllib3                  # retrieve path xml
import xml.etree.ElementTree    # analyse path xml
import pymongo                  # store path/person data
import random
# import custom helpers
from helpers import *

# preset text / printing
X_GENERATING = "Generating..."
X_GEN_LOC = "Please generate location data."
X_DONE = "Done"
X_ERROR = "Error"


class Generator(object):

    def __init__(self):
        """
            People Generator.
        """

        self.person = Person()
        self.location = PostCodes()

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

        # movement types
        self.transport = ['Car', 'Pedestrian', 'Bicycle', 'HeavyVehicle']

        # window management
        self.root = Tk()
        self.root.minsize(240, 240)

        # visuals
        self.peopleCount = self.make_entry(self.root, "Amount:", bd=2)
        self.dbName = self.make_entry(self.root, "Database:", bd=2)

        #TODO: change to a more complex generate command
        self.generateButton = Button(
            self.root, text="GENERATE", command=self.generate_path
        )
        self.generateButton.pack(side=BOTTOM)


        # implement the time data, from travel times
        self.time_period = 7  # days            ################
        self.start_time = "01/01/2016 14:32"    # pymongo date #
        self.current_time = ""                  ################
        self.end_time = "now"


        self.tag = lambda x: "{http://www.opengis.net/gml}"+x

        self.pool = urllib3.PoolManager(1)

    def make_entry(self, parent, caption, **options):
        """Label/TextBox maker."""
        Label(parent, text=caption).pack(side=TOP)
        entry = Entry(parent, **options)
        entry.pack(side=TOP)
        return entry

    def _generate_points(self):
        pass

    def generate_path(self):
        """
        Generate whole traversal between points, within a real travel time.
        """
        print(X_GENERATING)

        # initialise location data
        self.location.generate_points()

        # starting point
        point_a = self.location.get_start()
        # ending point
        point_z = self.location.get_end()
        # via points
        waypoints = self.location.get_waypoints()

        print(point_a, point_z, waypoints)

        # current transportation type
        current_transport = random.choice(self.transport)
        print(current_transport)

        u = self.URL(point_a, point_z, waypoints, "Car")
        print(u)

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

        # TODO:
        # ? add POI to path, realistic movement to places.

        print(len(path))
        print(X_DONE)

        #TODO:
        # Add interchange points, for various mode of movement.
        # Add simulated time data.

    # start up the UI
    def launch(self):
        self.root.mainloop()


if __name__ == '__main__':
    g = Generator()
    g.generate_path()
