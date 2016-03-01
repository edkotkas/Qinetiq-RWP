from tkinter import *           # UI
from tkinter import messagebox
import pymongo                  # store path/person data
import random
from threading import Thread
# import custom helpers
from helpers import *


# preset text / printing
X_GEN_LOC = "Please generate location data."
X_ERROR = "Error"


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

        # window management
        self.root = Tk()

        # visuals
        self.peopleCount = self.make_entry(self.root, "Amount:", 1, bd=2)
        # self.dbName = self.make_entry(self.root, "Database:", bd=2)

        # TODO: change to a more complex generate command
        self.generateButton = Button(
            self.root, text="GENERATE",
            command=lambda: self.generate(int(self.peopleCount.get()))
        )
        self.generateButton.pack(side=BOTTOM)

        # implement the time data, from travel times
        self.time_period = 7  # days            ################
        self.start_time = "01/01/2016 14:32"    # pymongo date #
        self.current_time = ""                  ################
        self.end_time = "now"

    def make_entry(self, parent, caption, innert, **options):
        """Label/TextBox maker."""
        Label(parent, text=caption).pack(side=TOP)
        entry = Entry(parent, **options)
        entry.insert(END, innert)
        entry.pack(side=TOP)
        return entry

    def generate(self, amount):
        """Generate the travel db."""
        people = None
        for _ in range(amount):
            identifier, fname, lname = self.person.generate()
            visits = self.location.generate()

            self.mov.insert({
                "uniq_id": '%s' % identifier,
                "first_name": fname,
                "last_name": lname,
                "visits": str(visits)
            })

        # print(people)

        messagebox.showinfo("info", "Completed.")

    # start up the UI
    def launch(self):
        self.root.mainloop()


if __name__ == '__main__':
    g = Generator()
    g.launch()
