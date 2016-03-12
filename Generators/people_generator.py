import pymongo                  # store path/person data
import random
import time
import sys
import webbrowser
# import custom helpers
from helpers import *


class Generator(object):

    def __init__(self):
        """
            People Generator.
        """
        self.person = Person()
        self.location = Location()

        try:
            with open("Generators/helpers/.mdbpws", "r") as pws:
                _ip, _port = pws.readlines()
                _ip = _ip.strip()
                _port = int(_port.strip())
        except:
            raise Exception("Could not load data.")

        self.mongo = pymongo.MongoClient(_ip)   # , _port
        self.db = self.mongo.qinetiq
        self.mov = self.db.movement
        # self.people = self.db.people
        # self.gp = self.db.health

    def c_print(self,text):
        sys.stdout.write(str(text))
        sys.stdout.flush()

    def generate(self, amount):
        """Generate the travel db."""
        people = None
        print("Generating...")
        for index in range(amount):
            identifier, fname, lname = self.person.generate()
            visits = self.location.generate()
            self.c_print("%s/" % str(index+1))

            self.mov.insert({
                "uniq_id": '%s' % identifier,
                "visited": [{
                    "lat": x.split(" ")[1],
                    "lon": x.split(" ")[0],
                    "pingTime": t
                } for t, x in visits]
            })

            self.c_print("*")
            time.sleep(0.5)

        print("\nDone")


if __name__ == '__main__':
    g = Generator()
    g.generate(1)
