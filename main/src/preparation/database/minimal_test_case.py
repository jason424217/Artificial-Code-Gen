from pymongo import MongoClient
from datetime import datetime

# Connect to the database
client = MongoClient('localhost', 27017)
db = client.test  # The name of the database is test
collection = db.test_collection  # The name of the collection is test_collection

# Create a document (stored here as a dictionary) to insert into the database
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
record = {"testing?":"yes", "time":current_time }

# Insert the document
collection.insert_one(record)

# Query the database using a query dictionary.
# Here we are looking for records where the value of 'testing?' is 'no'. We just inserted into our db
# a record where 'testing?' was 'yes,' and so this query should return "No matches found"

check_if_in_collection = {"testing?": "no"}
in_collection = collection.count_documents(check_if_in_collection)

# Equally valid syntax would be "collection.find(check_if_in_collection)," but this would return a
# an iterable object instead.

if in_collection == 0:
    print("No matches found")

elif in_collection > 0:
    print(str(in_collection) + " matches found")
    print(in_collection)
