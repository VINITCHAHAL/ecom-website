import pymongo

url = 'mongodb://localhost:27017'
client = pymongo.MongoClient(url)

db=client['ecom_website']

# Function to return the database instance
def get_db():
    return db