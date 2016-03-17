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

        # movement data
        self.mov = self.db.movement

        # people data
        self.people = self.db.people

        # health data
        self.gp = self.db.health
        self.symptoms = [
            "sore throat",
            "fever",
            "fatigue",
            "muscle ache",
            "chest discomfort",
            "breathing difficulty",
            "nausea",
            "coughing up blood",
            "painful swallowing",
            "shock",
            "meningitis"
        ]
        self.symptoms = [
            *symptoms[:7]*100, *self.symptoms[7:]
        ]

    def c_print(self,text):
        sys.stdout.write(str(text))
        sys.stdout.flush()

    def generate(self, amount):
        """Generate the travel db."""
        print("Generating...")
        for index in range(amount):
            self.c_print("%s/" % str(index+1))

            self.person.generate()
            self.c_print("-")

            visits = self.location.generate()
            self.c_print("=")

            self.people.insert({
                "dateOfBirth": self.person.dob,
                "firstName": self.person.first_name,
                "lastName": self.person.last_name,
                "phoneNumber": self.person.phone,
                "password": self.person.password,
                "uid": self.person.unique_id
            })

            self.c_print("*")

            symptoms = list(set([
                random.choice(chance_leveler) \
                    for _ in range(
                        0, random.randint(
                            0, random.randint(
                                0, len(symptoms)
                            )
                        )
                    )
                ]
            ))

            self.gp.insert({
                "uid": '%s' % self.person.unique_id,
                "symptoms": ""
            })

            self.c_print("*")

            self.mov.insert({
                "uid": '%s' % self.person.unique_id,
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
