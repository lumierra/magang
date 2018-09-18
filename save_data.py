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


for i in range(31):
    data = SL.get_dataHarian('tekno', 'tekno', 2017, 1, i+1)
    attr = []
    for i in range(len(data)):
        attr.append(data[i])

    db.insert_data('scraper', 'tekno', attr)

    data = ST.get_dataHarian('tekno', 'tekno', 2017, 1, i + 1)
    attr = []
    for i in range(len(data)):
        attr.append(data[i])

    db.insert_data('scraper', 'tekno', attr)

    data = SK.get_dataHarian('tekno', 'tekno', 2017, 1, i + 1)
    attr = []
    for i in range(len(data)):
        attr.append(data[i])

    db.insert_data('scraper', 'tekno', attr)


# list_category_liputan = ['news', 'bisnis', 'bola', 'showbiz', 'tekno', 'otomotif']
# list_name_category_liputan = ['news', 'bisnis', 'sports', 'entertainment', 'tekno', 'otomotif']
#
# list_category_tempo = ['nasional', 'pemilu', 'pilpres', 'dunia', 'bisnis', 'bola', 'sport', 'seleb', 'tekno', 'otomotif']
# list_name_category_tempo = ['news', 'news', 'news', 'news', 'bisnis', 'sports', 'sports', 'entertainment', 'tekno', 'otomotif']


#delete data from mongoDB
# db.delete_dataDaily('scraper', 'test', 'liputan6.com')

#Get Data
# for x,y in zip(list_category_liputan, list_name_category_liputan):
#     data = SL.get_dataHarian(x, y, now.year, now.month, now.day)
#
#     attr = []
#     for i in range(len(data)):
#         attr.append(data[i])
#
#     db.insert_data('scraper', 'test', attr)


# data = SL.main()
#
# attr = []
# for i in range(len(data)):
#     attr.append(data[i])
#
# db.insert_data('scraper', 'test', attr)