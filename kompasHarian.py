import datetime
from Database.dbMongo import Database
from Scraper.kompas_scraper import Scraper_Kompas

SK = Scraper_Kompas()
db = Database()
now = datetime.datetime.now().date()

database = 'scraper'
collection = 'test'
source = 'kompas.com'

list_category_kompas = ['news', 'ekonomi', 'bola', 'entertainment', 'tekno', 'otomotif']
list_name_category_kompas = ['news', 'bisnis', 'sports', 'entertainment', 'tekno', 'otomotif']

#delete data from mongoDB
db.delete_dataDaily(database, collection, source)

#Get Data
for x,y in zip(list_category_kompas, list_name_category_kompas):
    data = SK.get_dataHarian(x, y, now.year, now.month, now.day)

    attr = []
    for i in range(len(data)):
        attr.append(data[i])

    db.insert_data(database, collection, attr)

data = SK.get_ner('harian', database, collection, source)
attr = []
for d in data:
    attr.append(d)
db.delete_dataDaily(database, collection, source)
db.insert_data(database, collection, attr)