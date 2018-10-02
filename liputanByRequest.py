import datetime
from Database.dbMongo import Database
from Scraper.liputan_scraper import Scraper_Liputan

SL = Scraper_Liputan()
db = Database()
now = datetime.datetime.now().date()

# list_category_tempo = ['nasional', 'pemilu', 'pilpres', 'dunia', 'bisnis', 'bola', 'sport', 'seleb', 'tekno', 'otomotif']
# list_name_category_tempo = ['news', 'news', 'news', 'news', 'bisnis', 'sports', 'sports', 'entertainment', 'tekno', 'otomotif']

status = 'harian'
database = 'scraper'
collection = 'tekno'
source = 'liputan6.com'
category = 'tekno'
name_category = 'tekno'
day = 31
month = 6
year = 2018

for i in range(31):

    #delete data from mongoDB
    db.delete_by_request(database, collection, source, i+1, month, year)

    # Get Data
    data = SL.get_dataHarian(category, name_category, year, month, i+1)

    attr = []
    for d in data:
        attr.append(d)

    db.insert_data(database, collection, attr)

    data = SL.get_ner2(database, collection, source, i+1, month, year)
    attr = []
    for d in data:
        attr.append(d)
    db.delete_by_request(database, collection, source, i+1, month, year)
    db.insert_data(database, collection, attr)