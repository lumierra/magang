import datetime
from Scraper.liputan_scraper import Scraper_Liputan
from Database.dbMongo import Database


SL = Scraper_Liputan()
db = Database()
now = datetime.datetime.now().date()

list_category_liputan = ['news', 'bisnis', 'bola', 'showbiz', 'tekno', 'otomotif']
list_name_category_liputan = ['news', 'bisnis', 'sports', 'entertainment', 'tekno', 'otomotif']

#delete data from mongoDB
db.delete_dataDaily('scraper', 'test')

#Get Data
for x,y in zip(list_category_liputan, list_name_category_liputan):
    data = SL.get_dataHarian(x, y, now.year, now.month, now.day)

    attr = []
    for i in range(len(data)):
        attr.append(data[i])

    db.insert_data('scraper', 'test', attr)


# data = SL.main()
#
# attr = []
# for i in range(len(data)):
#     attr.append(data[i])
#
# db.insert_data('scraper', 'test', attr)