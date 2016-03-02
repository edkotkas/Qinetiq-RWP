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

        try:
            with open("helpers/.mdbpws", "r") as pws:
                _ip, _port = pws.readlines()
                _ip = _ip.strip()
                _port = int(_port.strip())
        except:
            raise Exception("Could not load data.")

        self.mongo = pymongo.MongoClient(_ip, _port)
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

    def generate(self, amount, sample=False):
        """Generate the travel db."""
        people = None
        print("Generating...")
        for index in range(amount if not sample else 1):
            identifier, fname, lname = self.person.generate()
            visits = self.location.generate(sample)
            self.c_print("%s/" % str(index+1))

            if sample:
                print(self.location.sample_url)
            else:
                self.mov.insert({
                    "uniq_id": '%s' % identifier,
                    "first_name": fname,
                    "last_name": lname,
                    "visits": str(visits)
                })
                self.c_print("*")
                time.sleep(0.5)

        print("\nDone")


if __name__ == '__main__':
    g = Generator()
    g.generate(int(sys.argv[1]), bool(sys.argv[2]) if sys.argv[2] != None else False)
