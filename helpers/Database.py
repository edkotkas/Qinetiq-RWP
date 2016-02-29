if __name__ == '__main__':

    # establish MongoDB collection
    mdb = MongoClient()
    db = mdb.movement
    db.persons.drop()

    # generate helpers
    for i in range(100):
        name, locations = generate_person()

        for x in locations:
            entry = {
                "name": name,
                "visited": "%f %f" % x
            }
            print(entry)
            db.persons.insert_one(
                entry
            )

    print("Added to db.")
