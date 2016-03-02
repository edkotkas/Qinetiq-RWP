import pymongo                  # store path/person data
import random
import time
import sys
# import custom helpers
from helpers import *


class Generator(object):

    def __init__(self):
        """
            People Generator.
        """
        self.person = Person()
        self.location = Location()
        self.mongo = pymongo.MongoClient()
        self.db = self.mongo.qinetiq
        self.mov = self.db.movement

        # implement the time data, from travel times
        self.time_period = 7  # days            ################
        self.start_time = "01/01/2016 14:32"    # pymongo ISO #
        self.current_time = ""                  ################
        self.end_time = "now"

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
                "first_name": fname,
                "last_name": lname,
                "visits": str(visits)
            })
            time.sleep(0.5)
        print("\nDone")


if __name__ == '__main__':
    g = Generator()
    g.generate(int(sys.argv[1]))
