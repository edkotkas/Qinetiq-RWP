import uuid
import os
import random


class Person(object):

    def __init__(self):

        self._first_names = [
            fn.strip() for fn in \
                            open("Generators/helpers/info/first_names.txt").readlines()
        ]
        self._last_names = [
            ln.strip() for ln in \
                           open("Generators/helpers/info/last_names.txt").readlines()
        ]

        self._first_name = None
        self._last_name = None
        self._password = None
        self._phone = None
        self._unique_id = None

    def generate(self):
        """
        Generate a person with their unique identifier.
        """
        self._first_name = random.choice(self._first_names)
        self._last_name = random.choice(self._last_names)

        self._generate_uniqueid()

        return self.get_uniqueid(), self.get_firstName(), self.get_lastName()

    def get_firstName(self):
        return self._first_name

    def get_lastName(self):
        return self._last_name

    def _generate_uniqueid(self):
        self._unique_id = uuid.uuid5(
            uuid.uuid4(), "%s %s" % (self.get_firstName(), self.get_lastName())
        )

    def get_uniqueid(self):
        return self._unique_id


if __name__ == '__main__':
    p = Person()
    p.generate()
    print(p.get_uniqueid(), p.get_firstName(), p.get_lastName())
