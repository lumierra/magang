import id_aldo
import requests
import id_beritagar as indo
from spacy import displacy
from bs4 import BeautifulSoup
from tqdm import tqdm, tqdm_notebook
from Database.dbMongo import Database
from textacy.preprocess import preprocess_text

nlp = id_aldo.load()
nlp_ner = indo.load()
db = Database()
# fopen = open('id.stopwords.02.01.2016.txt', 'r')
#
# stopwords = fopen.read()

stopwords = requests.get(
    "https://raw.githubusercontent.com/masdevid/ID-Stopwords/master/id.stopwords.02.01.2016.txt").text.split("\n")


class Scraper_Tempo():

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

    def get_ner2(self, database=None, collection=None, source=None, day=None, month=None, year=None):

        query = db.get_dataByRequest(database, collection, source, day, month, year)

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
        for ent in doc.ents:
            if ent.end <= 5:
                n = ent.end_char + 1
            else:
                n = len(text)

        result = text[n:].strip()

        return result

    def get_content(self, url=None):
        data = []
        response = requests.get(url).text
        soup = BeautifulSoup(response, "html5lib")

        sub_category = soup.select('.breadcrumbs > li')[2].text
        img = soup.select_one('figure > a')['href']

        contents = soup.select('#isi > p')

        for content in contents:
            if content.text.strip()[:10] != 'Baca juga:' and content.text.strip()[:5] != 'Baca:':
                data.append(content.text.strip() + '\n\n')

        con = ''.join(data)
        con= preprocess_text(con, fix_unicode=True)
        con = self.ner_text(con)
        con2 = ''.join(data)
        con2 = self.ner_text(con2)
        con2 = con2.split('\n\n')

        data_json = {
            "sub_category": sub_category,
            "img": img,
            "content": con,
            "content_html": con2
        }

        return data_json

    def get_content2(self, all_data=None):
        for i in tqdm(range(len(all_data)), desc='Get Content'):
            try:
                temp = self.get_content(all_data[i]['url'])
                all_data[i]['content'] = temp['content']
                all_data[i]['content_html'] = temp['content_html']
                all_data[i]['img'] = temp['img']
                all_data[i]['sub_category'] = temp['sub_category']
                all_data[i]['description'] = all_data[i]['title'] + ' ' + all_data[i]['content'][:255] + '....'
            except:
                pass

        return all_data

    def clean_content(self, all_data=None):
        for i in tqdm(range(len(all_data)), desc='Clean Content'):
            text_stopword = []
            all_data[i]['clean_content'] = preprocess_text(all_data[i]['content'], lowercase=True, fix_unicode=True,
                                                           no_punct=True)
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

    def get_tempoDaily(self, category=None, name_category=None, year=None, month=None, day=None):

        data = []
        if month <= 9:
            if day <= 9:
                url = '''https://www.tempo.co/indeks/{}/0{}/0{}/{}'''.format(year, month, day, category)
            else:
                url = '''https://www.tempo.co/indeks/{}/0{}/{}/{}'''.format(year, month, day, category)
        else:
            if day <= 9:
                url = '''https://www.tempo.co/indeks/{}/{}/0{}/{}'''.format(year, month, day, category)
            else:
                url = '''https://www.tempo.co/indeks/{}/{}/{}/{}'''.format(year, month, day, category)

        print(url)
        response = requests.get(url).text
        soup = BeautifulSoup(response, "html5lib")
        contents = soup.select('.list.list-type-1 > ul > li')

        for i in range(len(contents)):
            url_lokal = contents[i].select_one('a')['href']
            title = contents[i].select_one('.title').text
            date = url.split('/')[6] + '-' + url.split('/')[5] + '-' + url.split('/')[4]

            data_json = {
                'category': name_category,
                'title': title,
                'description': '',
                'url': url_lokal,
                'content': '',
                'content_html': '',
                'img': '',
                'sub_category': '',
                'publishedAt': date,
                'source': 'tempo.co',
                'clean_content': '',
                'ner_content': '',
                'count_ner': {
                    'person': 0,
                    'org': 0,
                    'gpe': 0,
                    'event': 0,
                    'merk': 0,
                    'product': 0
                }
            }

            data.append(data_json)

        return data

    def get_tempoMonthly(self, category=None, name_category=None, year=None, month=None):

        data = []
        for i in tqdm(range(31), desc='Get Data'):
            try:
                if month <= 9:
                    if i + 1 <= 9:
                        url = '''https://www.tempo.co/indeks/{}/0{}/0{}/{}'''.format(year, month, i + 1, category)
                    else:
                        url = '''https://www.tempo.co/indeks/{}/0{}/{}/{}'''.format(year, month, i + 1, category)
                else:
                    if i + 1 <= 9:
                        url = '''https://www.tempo.co/indeks/{}/{}/0{}/{}'''.format(year, month, i + 1, category)
                    else:
                        url = '''https://www.tempo.co/indeks/{}/{}/{}/{}'''.format(year, month, i + 1, category)

                #             print(url)
                response = requests.get(url).text
                soup = BeautifulSoup(response, "html5lib")
                contents = soup.select('.list.list-type-1 > ul > li')

                for i in range(len(contents)):
                    url_lokal = contents[i].select_one('a')['href']
                    title = contents[i].select_one('.title').text
                    date = url.split('/')[6] + '-' + url.split('/')[5] + '-' + url.split('/')[4]

                    data_json = {
                        'category': name_category,
                        'title': title,
                        'description': '',
                        'url': url_lokal,
                        'content': '',
                        'content_html': '',
                        'img': '',
                        'sub_category': '',
                        'publishedAt': date,
                        'source': 'tempo.co',
                        'clean_content': '',
                        'ner_content': '',
                        'count_ner': {
                            'person': 0,
                            'org': 0,
                            'gpe': 0,
                            'event': 0,
                            'merk': 0,
                            'product': 0
                        }
                    }

                    data.append(data_json)
            except:
                pass

        return data

    def get_dataHarian(self, category=None, name_category=None, year=None, month=None, day=None):
        all_data = self.get_tempoDaily(category, name_category, year, month, day)
        all_data = self.get_content2((all_data))
        all_data = self.clean_data(all_data)
        all_data = self.clean_content(all_data)

        return all_data

    def get_dataBulanan(self, category=None, name_category=None, year=None, month=None):
        all_data = self.get_tempoMonthly(category, name_category, year, month)
        all_data = self.get_content2((all_data))
        all_data = self.clean_data(all_data)
        all_data = self.clean_content(all_data)

        return all_data

    def main(self):
        print(' ---- MENU SCRAPER TEMPO ---- ')
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
            db.delete_dataDaily('scraper', 'test', 'tempo.co')

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
            db.delete_dataDaily('scraper', 'test', 'tempo.co')
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
            db.delete_dataDaily('scraper', 'test', 'tempo.co')

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
            db.delete_dataDaily('scraper', 'test', 'tempo.co')
            db.insert_data('scraper', 'test', attr)

        else:
            print('Pilihan Tidak Ada !!')