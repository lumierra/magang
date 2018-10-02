import datetime
from Database.dbMongo import Database
from Scraper.tempo_scraper import Scraper_Tempo

ST = Scraper_Tempo()
db = Database()
now = datetime.datetime.now().date()

database = 'scraper'
collection = 'test'
source = 'tempo.co'

list_category_tempo = ['nasional', 'pemilu', 'pilpres', 'dunia', 'bisnis', 'bola', 'sport', 'seleb', 'tekno', 'otomotif']
list_name_category_tempo = ['news', 'news', 'news', 'news', 'bisnis', 'sports', 'sports', 'entertainment', 'tekno', 'otomotif']

#delete data from mongoDB
db.delete_dataDaily(database, collection, source)

# Get Data
for x,y in zip(list_category_tempo, list_name_category_tempo):
    data = ST.get_dataHarian(x, y, now.year, now.month, now.day)

    attr = []
    for i in range(len(data)):
        attr.append(data[i])

    db.insert_data(database, collection, attr)

data = ST.get_ner('harian', database, collection, source)
attr = []
for d in data:
    attr.append(d)
db.delete_dataDaily(database, collection, source)
db.insert_data(database, collection, attr)