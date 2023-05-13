# mongoClient = 'localhost:27017'
import os


mongoClient = os.environ.get('MONGODB_URI')
dbName = 'LISTED_STOCKS'
