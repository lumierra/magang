import datetime
from Database.dbMongo import Database
from Scraper.tempo_scraper import Scraper_Tempo

ST = Scraper_Tempo()
db = Database()
now = datetime.datetime.now().date()

# list_category_tempo = ['nasional', 'pemilu', 'pilpres', 'dunia', 'bisnis', 'bola', 'sport', 'seleb', 'tekno', 'otomotif']
# list_name_category_tempo = ['news', 'news', 'news', 'news', 'bisnis', 'sports', 'sports', 'entertainment', 'tekno', 'otomotif']

database = 'scraper'
collection = 'tekno'
source = 'tempo.co'
category = 'tekno'
name_category = 'tekno'
day = 1
month = 1
year = 2017

#delete data from mongoDB
db.delete_by_request(database, collection, source, day, month, year)

# Get Data
data = ST.get_dataHarian(category, name_category, year, month, day)

attr = []
for i in range(len(data)):
    attr.append(data[i])

db.insert_data(database, collection, attr)

data = ST.get_ner('harian')
attr = []
for d in data:
    attr.append(d)
db.delete_by_request(database, collection, source, day, month, year)
db.insert_data(database, collection, attr)