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

    def get_ner(self):

        query = db.get_data('scraper', 'test', 'tempo.co')

        all_data = []
        for q in query:
            all_data.append(q)

        for i in range(len(all_data)):
            text = all_data[i]['content']
            text = text.replace('\n', '').replace('    ', '')
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
            if content.text.strip()[:10] != 'Baca juga:':
                data.append(content.text.strip())

        p = ''.join(data)
        p = preprocess_text(p, fix_unicode=True)
        p = self.ner_text(p)

        data_json = {
            "sub_category": sub_category,
            "img": img,
            "content": p,
        }

        return data_json

    def get_content2(self, all_data=None):
        print('Get Content...')

        for i in tqdm(range(len(all_data))):
            try:
                temp = self.get_content(all_data[i]['url'])
                all_data[i]['content'] = temp['content']
                all_data[i]['img'] = temp['img']
                all_data[i]['sub_category'] = temp['sub_category']
                all_data[i]['description'] = all_data[i]['title'] + ' ' + all_data[i]['content'][:255] + '....'
            except:
                pass

        return all_data

    def clean_content(self, all_data=None):
        print('Clean Content')
        for i in tqdm(range(len(all_data))):
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

    def get_dataHarian(self, category=None, name_category=None, year=None, month=None, day=None):
        all_data = self.get_tempoDaily(category, name_category, year, month, day)
        all_data = self.get_content2((all_data))
        all_data = self.clean_data(all_data)
        all_data = self.clean_content(all_data)

        return all_data