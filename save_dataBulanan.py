from Scraper.liputan_scraper2 import Scraper_Liputan
from Database.dbMongo import Database


SL = Scraper_Liputan()
db = Database()

#Get Data
data = SL.main()

attr = []
for i in range(len(data)):
    attr.append(data[i])

db.insert_data('scraper', 'test', attr)