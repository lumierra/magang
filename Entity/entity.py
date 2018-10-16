import pymongo
import datetime
import id_beritagar
from tqdm import tqdm
from collections import Counter

today = datetime.date.today()
year = today.year
month = today.month
day = today.day

database = 'scraper'
collection = 'topEntity'

nlp = id_beritagar.load()

class Entity(object):
    def __init__(self):
        self

    def insert_top_entity(self, database=None, collection=None, attr=None):
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client["{}".format(database)]
        col = db["{}".format(collection)]

        try:
            insert_db = col.insert(attr)
            print('Insert Data into MongoDB Succesfully')
        except:
            print('Insert Data into MongoDB Failed')

    def get_query(self):
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client.scraper
        col = db.test
        query = col.find({
            'publishedAt': '{}-{}-{}'.format(day,month,year)
        })
        data = []
        for q in query:
            data.append(q)

        return data

    def delete_dataDaily(self):
        client = pymongo.MongoClient("mongodb://localhost:27017")
        db = client.scraper
        col = db.topEntity

        if month <= 9:
            if day <= 9:
                query = col.remove({
                    'publishedAt': '0{}-0{}-{}'.format(day, month, year)
                })
            else:
                query = col.remove({
                    'publishedAt': '{}-0{}-{}'.format(day, month, year)
                })
        else:
            if day <= 9:
                query = col.remove({
                    'publishedAt': '0{}-{}-{}'.format(day, month, year)
                })
            else:
                query = col.remove({
                    'publishedAt': '{}-{}-{}'.format(day, month, year)
                })

        return query

    def get_ner(self, all_data):
        data = []
        for ad in tqdm(all_data, desc='Top Entity'):
            doc = nlp(ad['content'])
            for ent in doc.ents:
                data.append(ent.text)

        for i in range(len(data)):
            if '\n' in data[i]:
                data[i] = data[i].replace('\n', '')

        return data

    def get_counter(self, all_data):
        data = []
        for ad in all_data:
            if ad != '':
                data.append(ad)

        return data

    def set_json(self, all_data):
        data_json = {
            'publishedAt': '{}-{}-{}'.format(day,month,year),
            'top_ner': all_data
        }

        return  data_json

    def top_entity(self):
        self.delete_dataDaily()
        entity = self.get_query()
        entity = self.get_ner(entity)
        entity = self.get_counter(entity)
        entity = Counter(entity)
        entity = entity.most_common(30)
        entity = self.set_json(entity)

        self.insert_top_entity(database, collection, entity)

