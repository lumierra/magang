import datetime
from Database.dbMongo import Database
from Scraper.liputan_scraper import Scraper_Liputan
from Scraper.tempo_scraper import Scraper_Tempo
from Scraper.kompas_scraper import Scraper_Kompas


SL = Scraper_Liputan()
ST = Scraper_Tempo()
SK = Scraper_Kompas()

db = Database()
now = datetime.datetime.now().date()

#delete data from mongoDB
db.delete_dataDaily('scraper', 'test', 'tempo.co')

list_category_liputan = ['tekno']
list_name_category_liputan = ['tekno']

# Get Data
for x,y in zip(list_category_liputan, list_name_category_liputan):
    data = ST.get_dataHarian(x, y, now.year, now.month, now.day)

    attr = []
    for i in range(len(data)):
        attr.append(data[i])

    db.insert_data('scraper', 'test', attr)

data = ST.get_ner()
attr = []
for d in data:
    attr.append(d)
db.delete_dataDaily('scraper', 'test', 'tempo.co')
db.insert_data('scraper', 'test', attr)