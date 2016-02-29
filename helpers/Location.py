import json
import random


class PostCodes(object):

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

        # starting point
        self.start_point = None

        # ending point
        self.end_point = None

        # waypoints between
        self.waypoints = None

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
        self.waypoints = "%20".join(
            [
                "%f,%f" % random.choice(self.area) for _ in range(way_amount)
            ]
        )



    def get_waypoints(self):
        return self.waypoints

    def get_start(self):
        return self.start_point

    def get_end(self):
        return self.end_point


if __name__ == '__main__':
    l = PostCodes()
    l.generate_points()
    print(l.get_start(), l.get_end())
