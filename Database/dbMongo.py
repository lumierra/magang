import os
import yaml
import pymongo
import datetime
from pymongo.errors import ServerSelectionTimeoutError

filename_config = os.path.abspath("Config/config.yml")
config = yaml.load(open(filename_config, "r"))

now = datetime.datetime.now().date()

class Database():
    def __init__(self):
        self.host = config['database']['mongo']['host']
        self.database = config['database']['mongo']['database']
        self.port = config['database']['mongo']['port']
        self.config = config

    def test_connection(self):

        client = pymongo.MongoClient("mongodb://{}:{}".format(self.host, self.port), serverSelectionTimeoutMS=10, connectTimeoutMS=20000)

        try:
            print(client.server_info())
        except ServerSelectionTimeoutError:
            print("server is down.")

    def insert_data(self, database=None, collection=None, attr=None):
        myclient = pymongo.MongoClient("mongodb://{}:{}".format(self.host, self.port))
        mydb = myclient["{}".format(database)]
        mycol = mydb["{}".format(collection)]

        try:
            insert_db = mycol.insert_many(attr)
            print('Insert Data into MongoDB Succesfully')
        except:
            print('Insert Data into MongoDB Failed')

    def find_data(self, database=None, collection=None):
        myclient = pymongo.MongoClient("mongodb://{}:{}".format(self.host, self.port))
        mydb = myclient["{}".format(database)]
        mycol = mydb["{}".format(collection)]

        query = {
            "category": "otomotif"
        }

        doc = mycol.delete_many(query)

    def delete_dataDaily(self, database=None, collection=None, source=None):
        myclient = pymongo.MongoClient("mongodb://{}:{}".format(self.host, self.port))
        mydb = myclient["{}".format(database)]
        mycol = mydb["{}".format(collection)]

        year = now.year
        month = now.month
        day = now.day

        if month <= 9:
            if day <= 9:
                query = mycol.remove({
                    'publishedAt': '0{}-0{}-{}'.format(day, month, year),
                    'source' : source
                })
            else:
                query = mycol.remove({
                    'publishedAt': '{}-0{}-{}'.format(day, month, year),
                    'source': source
                })
        else:
            if day <= 9:
                query = mycol.remove({
                    'publishedAt': '0{}-{}-{}'.format(day, month, year),
                    'source': source
                })
            else:
                query = mycol.remove({
                    'publishedAt': '{}-{}-{}'.format(day, month, year),
                    'source': source
                })

    def delete_dataMonthly(self, database=None, collection=None, source=None, month=None, year=None):
        myclient = pymongo.MongoClient("mongodb://{}:{}".format(self.host, self.port))
        mydb = myclient["{}".format(database)]
        mycol = mydb["{}".format(collection)]

        query = mycol.find({
            'source': source,
            'publishedAt': {
                '$gte': '01-{}-{}'.format(month, year),
                '$lte': '31-{}-{}'.format(month, year)
            }
        })

        return query

    def get_data(self, database=None, collection=None, source=None):
        myclient = pymongo.MongoClient("mongodb://{}:{}".format(self.host, self.port))
        mydb = myclient["{}".format(database)]
        mycol = mydb["{}".format(collection)]

        year = now.year
        month = now.month
        day = now.day

        if month <= 9:
            if day <= 9:
                query = mycol.find({
                    'publishedAt': '0{}-0{}-{}'.format(day, month, year),
                    'source' : source
                })
            else:
                query = mycol.find({
                    'publishedAt': '{}-0{}-{}'.format(day, month, year),
                    'source': source
                })
        else:
            if day <= 9:
                query = mycol.find({
                    'publishedAt': '0{}-{}-{}'.format(day, month, year),
                    'source': source
                })
            else:
                query = mycol.find({
                    'publishedAt': '{}-{}-{}'.format(day, month, year),
                    'source': source
                })

        return query

    def get_dataMonthly(self, database=None, collection=None, source=None, month=None, year=None):
        myclient = pymongo.MongoClient("mongodb://{}:{}".format(self.host, self.port))
        mydb = myclient["{}".format(database)]
        mycol = mydb["{}".format(collection)]

        query = mycol.find({
            'source' : source,
            'publishedAt': {
                '$gte': '01-{}-{}'.format(month, year),
                '$lte': '31-{}-{}'.format(month, year)
            }
        })

        return query