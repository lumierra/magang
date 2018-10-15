import datetime
from Database.dbMongo import Database
from Scraper.liputan_scraper import Scraper_Liputan


SL = Scraper_Liputan()
db = Database()
now = datetime.datetime.now().date()

database = 'scraper'
collection = 'test'
source = 'liputan6.com'

list_category_liputan = ['news', 'bisnis', 'bola', 'showbiz', 'tekno', 'otomotif']
list_name_category_liputan = ['news', 'bisnis', 'sports', 'entertainment', 'tekno', 'otomotif']

#delete data from mongoDB
db.delete_dataDaily(database, collection, source)

#Get Data
for x,y in zip(list_category_liputan, list_name_category_liputan):
    data = SL.get_dataHarian(x, y, now.year, now.month, now.day)

    attr = []
    for i in range(len(data)):
        attr.append(data[i])

    db.insert_data(database, collection, attr)

data = SL.get_ner()
attr = []
for d in data:
    attr.append(d)
db.delete_dataDaily(database, collection, source)
db.insert_data(database, collection, attr)