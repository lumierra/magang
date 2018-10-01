import datetime
from Database.dbMongo import Database
from Scraper.tempo_scraper import Scraper_Tempo

ST = Scraper_Tempo()
db = Database()
now = datetime.datetime.now().date()

list_category_tempo = ['otomotif']
list_name_category_tempo = ['otomotif']

#delete data from mongoDB
# db.delete_dataMonthly('scraper', 'test2', 'tempo.co', '10', '2018')

# Get Data
# for x,y in zip(list_category_tempo, list_name_category_tempo):
#     data = ST.get_dataBulanan(x, y, now.year, now.month)
#
#     attr = []
#     for i in range(len(data)):
#         attr.append(data[i])
#
#     db.insert_data('scraper', 'test2', attr)

# data = ST.get_ner('bulanan')
# attr = []
# for d in data:
#     attr.append(d)
# db.delete_dataMonthly('scraper', 'test2', 'tempo.co', '10', '2018')
# db.insert_data('scraper', 'test2', attr)

data = ST.get_dataBulanan('tekno', 'tekno', 2018, 10)
print(data[0])