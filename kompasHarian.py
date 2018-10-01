import datetime
from Database.dbMongo import Database
from Scraper.kompas_scraper import Scraper_Kompas

SK = Scraper_Kompas()
db = Database()
now = datetime.datetime.now().date()

list_category_kompas = ['news', 'ekonomi', 'bola', 'entertainment', 'tekno', 'otomotif']
list_name_category_kompas = ['news', 'bisnis', 'sports', 'entertainment', 'tekno', 'otomotif']

#delete data from mongoDB
db.delete_dataDaily('scraper', 'test', 'kompas.com')

#Get Data
for x,y in zip(list_category_kompas, list_name_category_kompas):
    data = SK.get_dataHarian(x, y, now.year, now.month, now.day)

    attr = []
    for i in range(len(data)):
        attr.append(data[i])

    db.insert_data('scraper', 'test', attr)

data = SK.get_ner()
attr = []
for d in data:
    attr.append(d)
db.delete_dataDaily('scraper', 'test', 'kompas.com')
db.insert_data('scraper', 'test', attr)