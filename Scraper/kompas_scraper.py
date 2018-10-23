import id_aldo
import requests
import datetime
import id_beritagar as indo
from spacy import displacy
from Database.dbMongo import Database
from bs4 import BeautifulSoup
from tqdm import tqdm, tqdm_notebook
from textacy.preprocess import preprocess_text

db = Database()
nlp = id_aldo.load()
nlp_ner = indo.load()
# fopen = open('id.stopwords.02.01.2016.txt', 'r')
#
# stopwords = fopen.read()

stopwords = requests.get("https://raw.githubusercontent.com/masdevid/ID-Stopwords/master/id.stopwords.02.01.2016.txt").text.split("\n")


class Scraper_Kompas():

    def __init__(self):
        self

    def get_ner(self, status=None, database=None, collection=None, source=None):

        # if status == 'harian':
        #     query = db.get_data(database, collection, source)
        # else:
        #     query = db.get_dataMonthly('scraper', 'test2', 'tempo.co', '10', '2018')

        query = db.get_data(database, collection, source)

        all_data = []
        for q in query:
            all_data.append(q)

        for i in range(len(all_data)):
            text = all_data[i]['content'].split('\n')
            temp = []
            for t in text:
                temp.append(t + '\n')
            text = ''.join(temp)
            doc = nlp_ner(text)

            PERSON, ORG, GPE, EVENT, MERK, PRODUCT = 0, 0, 0, 0, 0, 0
            for ent in doc.ents:
                if ent.label_ == 'PERSON':
                    PERSON += 1
                elif ent.label_ == 'ORG':
                    ORG += 1
                elif ent.label_ == 'GPE':
                    GPE += 1
                elif ent.label_ == 'EVENT':
                    EVENT += 1
                elif ent.label_ == 'MERK':
                    MERK += 1
                elif ent.label_ == 'PRODUCT':
                    PRODUCT += 1

            all_data[i]['count_ner']['person'] = PERSON
            all_data[i]['count_ner']['org'] = ORG
            all_data[i]['count_ner']['gpe'] = GPE
            all_data[i]['count_ner']['event'] = EVENT
            all_data[i]['count_ner']['merk'] = MERK
            all_data[i]['count_ner']['product'] = PRODUCT

            data = []
            for ent in doc.ents:
                data_json = {
                    'text': ent.text,
                    'label': ent.label_
                }
                data.append(data_json)
            unique = {each['text']: each for each in data}.values()
            data = []
            for u in unique:
                data.append(u)

            for d in data:
                text = text.replace(d['text'],
                                    '''<mark class="{label}-{_id} font-mark transparent style-{label}"> {text} </mark>'''.format(
                                        _id=all_data[i]['_id'], label=d['label'], text=d['text']))
            text = ''.join(('''<div class="entities"> ''', text, ' </div>'))
            text = text.split('\n')

            all_data[i]['ner_content'] = text

        return all_data

    def ner_text(self, text=None):
        doc = nlp(text)
        #     displacy.render(doc, style='ent', jupyter=True)

        n = 0
        temp = 0
        for ent in doc.ents:
            if ent.end <= 1:
                n = ent.end_char
            elif (ent.end > 6 and ent.end <= 8):
                n = temp
            elif ent.end > 9:
                n = temp
            else:
                temp = n
                n = ent.end_char + 1

        result = text[n:].strip()

        return result

    def get_content(self, url=None):
        response = requests.get(url).text
        soup = BeautifulSoup(response, "html5lib")

        contents = soup.select_one('.photo > img')
        contents2 = soup.select('.read__content > p')

        temp_img = contents['src']

        data = []
        for i in range(len(contents2)):
            if contents2[i].text != '':
                if (contents2[i].text[:9] != 'Baca juga' and contents2[i].text[:5] != 'Baca:') \
                        and (contents2[i].text[:15] != 'We are thrilled') and (contents2[i].text[:6] != 'Flinke') \
                        and (contents2[i].text[:18] != 'Baca selengkapnya:') and (contents2[i].text[:25]) != 'Baca berita selengkapnya:' \
                        and (contents2[i].text[:7]) != 'Sumber:':
                    data.append(contents2[i].text  + '\n\n')

        con = ''.join(data)
        con = preprocess_text(con, fix_unicode=True)
        con = self.ner_text(con)
        con2 = ''.join(data)
        con2 = self.ner_text(con2)
        con2 = con2.split('\n\n')

        data_json = {
            "img": temp_img,
            "content": con,
            "content_html": con2
        }

        return data_json

    def get_content2(self, all_data=None):
        for i in tqdm(range(len(all_data))):
            try:
                temp = self.get_content(all_data[i]['url'])
                all_data[i]['content'] = temp['content']
                all_data[i]['content_html'] = temp['content_html']
                all_data[i]['img'] = temp['img']
                all_data[i]['description'] = all_data[i]['title'] + ' ' + all_data[i]['content'][:255] + '....'
            except:
                pass

        return all_data

    def clean_content(self, all_data=None):
        for i in tqdm(range(len(all_data)), desc='Clean Content'):
            text_stopword = []
            all_data[i]['clean_content'] = preprocess_text(all_data[i]['content'], lowercase=True, fix_unicode=True,no_punct=True)
            clean_content = all_data[i]['clean_content'].split()

            [text_stopword.append(cc) for cc in clean_content if cc not in stopwords]

            all_data[i]['clean_content'] = ' '.join(text_stopword)

        return all_data

    def clean_data(self, all_data=None):
        all_data2 = []
        for ad in all_data:
            if ad['content'] != '':
                all_data2.append(ad)

        return all_data2

    def get_dataMonthly(self, global_category=None, name_category=None, tahun=None, bulan=None):
        all_data = []
        for tanggal in tqdm(range(31), desc='Get Data Monthly'):
            try:
                url = '''https://{}.kompas.com/search/{}-{}-{}'''.format(global_category, tahun, bulan, tanggal + 1)
                data = requests.get(url)
                html = data.text
                soup = BeautifulSoup(html, "html5lib")
                count_page = soup.select('.paging__wrap.clearfix > .paging__item')

                if count_page == []:
                    url_lokal = '''https://{}.kompas.com/search/{}-{}-{}'''.format(global_category, tahun, bulan,
                                                                                   tanggal + 1)
                    data = requests.get(url_lokal)
                    html = data.text
                    soup = BeautifulSoup(html, "html5lib")

                    contents = soup.select('.article__list.clearfix')
                    print(url_lokal)

                    for content in contents:
                        try:
                            temp_category = content.select_one('.article__subtitle').text.strip()
                            temp_url = content.select_one('.article__link')['href']
                            temp_title = content.select_one('.article__link').text.strip()
                            temp_date = content.select_one('.article__date').text.replace(',', '').split()[0]
                            temp_date = datetime.datetime.strptime(temp_date, "%d/%m/%Y").strftime("%d-%m-%Y")

                            data_json = {
                                "category": name_category,
                                "title": temp_title,
                                "description": '',
                                "url": temp_url,
                                "content": '',
                                "content_html": '',
                                "img": '',
                                "sub_category": temp_category,
                                "publishedAt": temp_date,
                                "source": 'kompas.com',
                                "clean_content": '',
                                "ner_content": '',
                                'count_ner': {
                                    'person': 0,
                                    'org': 0,
                                    'gpe': 0,
                                    'event': 0,
                                    'merk': 0,
                                    'product': 0
                                }

                            }

                            all_data.append(data_json)

                        except:
                            pass
                else:
                    total_page = int(count_page[len(count_page) - 1].select('.paging__link')[0]['data-ci-pagination-page'])

                    for y in range(total_page):
                        try:
                            url_lokal = '''https://{}.kompas.com/search/{}-{}-{}/{}'''.format(global_category, tahun, bulan,
                                                                                              tanggal + 1, y + 1)
                            data = requests.get(url_lokal)
                            html = data.text
                            soup = BeautifulSoup(html, "html5lib")

                            contents = soup.select('.article__list.clearfix')
                            print(url_lokal)

                            for content in contents:
                                try:
                                    temp_category = content.select_one('.article__subtitle').text.strip()
                                    temp_url = content.select_one('.article__link')['href']
                                    temp_title = content.select_one('.article__link').text.strip()
                                    temp_date = content.select_one('.article__date').text.replace(',', '').split()[0]
                                    temp_date = datetime.datetime.strptime(temp_date, "%d/%m/%Y").strftime("%d-%m-%Y")

                                    data_json = {
                                        "category": name_category,
                                        "title": temp_title,
                                        "description": '',
                                        "url": temp_url,
                                        "content": '',
                                        "content_html": '',
                                        "img": '',
                                        "sub_category": temp_category,
                                        "publishedAt": temp_date,
                                        "source": 'kompas.com',
                                        "clean_content": '',
                                        "ner_content": '',
                                        'count_ner': {
                                            'person': 0,
                                            'org': 0,
                                            'gpe': 0,
                                            'event': 0,
                                            'merk': 0,
                                            'product': 0
                                        }
                                    }

                                    all_data.append(data_json)

                                except:
                                    pass
                        except:
                            pass
            except:
                pass

        return all_data

    def get_dataDaily(self, global_category=None, name_category=None, tahun=None, bulan=None, tanggal=None):
        all_data = []
        url = '''https://{}.kompas.com/search/{}-{}-{}'''.format(global_category, tahun, bulan, tanggal)
        data = requests.get(url)
        html = data.text
        soup = BeautifulSoup(html, "html5lib")
        count_page = soup.select('.paging__wrap.clearfix > .paging__item')

        if count_page == []:
            url_lokal = '''https://{}.kompas.com/search/{}-{}-{}'''.format(global_category, tahun, bulan, tanggal)
            data = requests.get(url_lokal)
            html = data.text
            soup = BeautifulSoup(html, "html5lib")

            contents = soup.select('.article__list.clearfix')
            print(url_lokal)

            for content in contents:
                try:
                    temp_category = content.select_one('.article__subtitle').text.strip()
                    temp_url = content.select_one('.article__link')['href']
                    temp_title = content.select_one('.article__link').text.strip()
                    temp_date = content.select_one('.article__date').text.replace(',', '').split()[0]
                    temp_date = datetime.datetime.strptime(temp_date, "%d/%m/%Y").strftime("%d-%m-%Y")

                    data_json = {
                        "category": name_category,
                        "title": temp_title,
                        "description": '',
                        "url": temp_url,
                        "content": '',
                        "content_html": '',
                        "img": '',
                        "sub_category": temp_category,
                        "publishedAt": temp_date,
                        "source": 'kompas.com',
                        "clean_content": '',
                        "ner_content": '',
                        'count_ner': {
                            'person': 0,
                            'org': 0,
                            'gpe': 0,
                            'event': 0,
                            'merk': 0,
                            'product': 0
                        }
                    }

                    all_data.append(data_json)

                except:
                    pass
        else:
            total_page = int(count_page[len(count_page) - 1].select('.paging__link')[0]['data-ci-pagination-page'])

            for y in range(total_page):
                try:
                    url_lokal = '''https://{}.kompas.com/search/{}-{}-{}/{}'''.format(global_category, tahun, bulan,
                                                                                      tanggal, y + 1)
                    data = requests.get(url_lokal)
                    html = data.text
                    soup = BeautifulSoup(html, "html5lib")

                    contents = soup.select('.article__list.clearfix')
                    print(url_lokal)

                    for content in contents:
                        try:
                            temp_category = content.select_one('.article__subtitle').text.strip()
                            temp_url = content.select_one('.article__link')['href']
                            temp_title = content.select_one('.article__link').text.strip()
                            temp_date = content.select_one('.article__date').text.replace(',', '').split()[0]
                            temp_date = datetime.datetime.strptime(temp_date, "%d/%m/%Y").strftime("%d-%m-%Y")

                            data_json = {
                                "category": name_category,
                                "title": temp_title,
                                "description": '',
                                "url": temp_url,
                                "content": '',
                                "content_html": '',
                                "img": '',
                                "sub_category": temp_category,
                                "publishedAt": temp_date,
                                "source": 'kompas.com',
                                "clean_content": '',
                                "ner_content": '',
                                'count_ner': {
                                    'person': 0,
                                    'org': 0,
                                    'gpe': 0,
                                    'event': 0,
                                    'merk': 0,
                                    'product': 0
                                }
                            }

                            all_data.append(data_json)

                        except:
                            pass
                except:
                    pass

        return all_data

    def get_dataHarian(self, category=None, name_category=None, year=None, month=None, day=None):
        all_data = self.get_dataDaily(category, name_category, year, month, day)
        all_data = self.get_content2(all_data)
        all_data = self.clean_data(all_data)
        all_data = self.clean_content(all_data)

        return all_data

    def get_dataBulanan(self, category=None, name_category=None, year=None, month=None):
        all_data = self.get_dataMonthly(category, name_category, year, month)
        all_data = self.get_content2(all_data)
        all_data = self.clean_data(all_data)
        all_data = self.clean_content(all_data)

        return all_data

    def main(self):
        print(' ---- MENU SCRAPER KOMPAS ---- ')
        print('1. Bulanan ')
        print('2. Harian ')
        pilihan = eval(input('Pilihan : '))

        if pilihan == 1:
            list_category = []
            list_name_of_category = []
            count = 0
            long_category = eval(input(' Banyaknya Kategori : '))
            while (count < long_category):
                category = input('Category : ')
                name_category = input('Name of Category : ')
                list_category.append(category)
                list_name_of_category.append(name_category)
                count += 1
            year = eval(input('Tahun : '))
            month = eval(input('Bulan : '))

            # delete data from mongoDB
            db.delete_dataDaily('scraper', 'test', 'kompas.com')

            # Get Data
            for x, y in zip(list_category, list_name_of_category):
                data = self.get_dataBulanan(x, y, year, month)

                attr = []
                for i in range(len(data)):
                    attr.append(data[i])

                db.insert_data('scraper', 'test', attr)

            data = self.get_ner()
            attr = []
            for d in data:
                attr.append(d)
            db.delete_dataDaily('scraper', 'test', 'kompas.com')
            db.insert_data('scraper', 'test', attr)

        elif pilihan == 2:
            list_category = []
            list_name_of_category = []
            count = 0
            long_category = eval(input(' Banyaknya Kategori : '))
            while (count < long_category):
                category = input('Category : ')
                name_category = input('Name of Category : ')
                list_category.append(category)
                list_name_of_category.append(name_category)
                count += 1
            year = eval(input('Tahun : '))
            month = eval(input('Bulan : '))
            day = eval(input('Tanggal : '))

            # delete data from mongoDB
            db.delete_dataDaily('scraper', 'test', 'kompas.com')

            # Get Data
            for x, y in zip(list_category, list_name_of_category):
                data = self.get_dataHarian(x, y, year, month, day)

                attr = []
                for i in range(len(data)):
                    attr.append(data[i])

                db.insert_data('scraper', 'test', attr)

            data = self.get_ner()
            attr = []
            for d in data:
                attr.append(d)
            db.delete_dataDaily('scraper', 'test', 'kompas.com')
            db.insert_data('scraper', 'test', attr)

        else:
            print('Pilihan Tidak Ada !!')


# if __name__== "__main__":
#     main()
