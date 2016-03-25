import uuid
import os
import random
import string
import datetime
import os

class Person(object):

    def __init__(self):
        cwd = os.getcwd()
        self.first_names = [
            fn.strip() for fn in \
                open(cwd+"/helpers/info/first_names.txt").readlines()
        ]
        self.last_names = [
            ln.strip() for ln in \
                open(cwd+"/helpers/info/last_names.txt").readlines()
        ]

        self.first_name = None
        self.last_name = None

        self.password = None
        self.phone = None
        self.dob = None
        self.unique_id = None

    def generate(self):
        """
        Generate a person with their unique identifier.
        """
        self.first_name = random.choice(self.first_names)
        self.last_name = random.choice(self.last_names)

        self.password = ''.join(
            random.choice(
                string.digits + string.ascii_letters
            ) for _ in range(8)
        )

        p1 = ["0","7"]
        p2 = [str(random.randint(0, 9)) for _ in range(3)]
        p3 = [str(random.randint(0, 9)) for _ in range(3)]
        p4 = [str(random.randint(0, 9)) for _ in range(3)]
        self.phone = ''.join(p1+p2+p3+p4)

        y = random.randint(1980, 1998)
        m = random.randint(1, 12)
        d = random.randint(1, 28)
        h = random.randint(0, 23)
        M = random.randint(0, 59)
        s = random.randint(0, 59)

        self.dob = datetime.datetime(y, m, d, h, M, s)

        self.unique_id = uuid.uuid5(
            uuid.UUID('e4939ddb-1dcd-4cfb-b71f-903e18160ef6'),
            "%s %s %s" % (self.first_name, self.last_name, self.password)
        )

if __name__ == '__main__':
    p = Person()
    p.generate()
    print(p.first_name, p.last_name, p.phone, p.dob, p.unique_id, p.password)
