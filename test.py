from Scraper.tempo_scraper import Scraper_Tempo
from Database.dbMongo import Database
import datetime

ST = Scraper_Tempo()
db = Database()
now = datetime.datetime.now().date()

query = db.get_data('scraper', 'test', 'tempo.co')
#
# for q in query[:1]:
#     print(q)

data = ST.get_ner2()
