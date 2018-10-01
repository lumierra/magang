import id_aldo
import requests
import id_beritagar as indo
from spacy import displacy
from bs4 import BeautifulSoup
from tqdm import tqdm, tqdm_notebook
from Database.dbMongo import Database
from textacy.preprocess import preprocess_text


# fopen = open('id.stopwords.02.01.2016.txt', 'r')
#
# stopwords = fopen.read()

stopwords = requests.get("https://raw.githubusercontent.com/masdevid/ID-Stopwords/master/id.stopwords.02.01.2016.txt").text.split("\n")

nlp = id_aldo.load()
nlp_ner = indo.load()
db = Database()

class Scraper_Liputan():

    def __init__(self):
        self

    def get_ner(self):

        query = db.get_data('scraper', 'test', 'liputan6.com')

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

        img = soup.select_one('.read-page--photo-gallery--item__picture > img')['data-src']
        contents = soup.select('.article-content-body__item-content > p')

        for i in range(len(contents)):
            if contents[i].text.strip() != '' and contents[i].text.strip()[:1] != '*' \
                    and contents[i].text.strip()[:8] != 'Reporter' and contents[i].text.strip()[:14] != 'Saksikan video'\
                    and contents[i].text.strip()[:1] != '(' and contents[i].text.strip()[:14] != 'Saksikan Video' \
                    and contents[i].text.strip()[:2] != ' (' and contents[i].text.strip()[:7] != 'Sumber:':
                data.append(contents[i].text.strip() + '\n\n')

        con = ''.join(data)
        con = preprocess_text(con, fix_unicode=True)
        con = self.ner_text(con)
        con2 = ''.join(data)
        con2 = self.ner_text(con2)
        con2 = con2.split('\n\n')

        data_json = {
            "img": img,
            "content": con,
            "content_html": con2
        }
        return data_json

    def get_content2(self, all_data=None):
        print('Get Content...')
        for i in tqdm(range(len(all_data))):
            try:
                temp = self.get_content(all_data[i]['url'])
                all_data[i]['content'] = temp['content']
                all_data[i]['img'] = temp['img']
                all_data[i]['content_html'] = temp['content_html']
            except:
                pass

        return all_data

    def clean_data(self, all_data=None):
        all_data2 = []
        for ad in all_data:
            if ad['content'] != '':
                all_data2.append(ad)

        return all_data2

    def clean_content(self, all_data=None):
        for i in tqdm(range(len(all_data)), desc='Clean Content'):
            text_stopword = []
            all_data[i]['clean_content'] = preprocess_text(all_data[i]['content'], lowercase=True, fix_unicode=True,no_punct=True)
            clean_content = all_data[i]['clean_content'].split()

            [text_stopword.append(cc) for cc in clean_content if cc not in stopwords]

            all_data[i]['clean_content'] = ' '.join(text_stopword)

        return all_data

    def get_dataMonthly(self, category=None, name_category=None, tahun=None, bulan=None):
        all_data = []
        for i in tqdm(range(31), desc='Get Data monthly'):
            for page in range(2):
                if bulan <= 9:
                    if i + 1 <= 9:
                        url = '''https://www.liputan6.com/{}/indeks/{}/0{}/0{}?page={}'''.format(category, tahun, bulan,
                                                                                                 i + 1, page + 1)
                    else:
                        url = '''https://www.liputan6.com/{}/indeks/{}/0{}/{}?page={}'''.format(category, tahun, bulan,
                                                                                                i + 1, page + 1)
                else:
                    if i + 1 <= 9:
                        url = '''https://www.liputan6.com/{}/indeks/{}/{}/0{}?page={}'''.format(category, tahun, bulan,
                                                                                                i + 1, page + 1)
                    else:
                        url = '''https://www.liputan6.com/{}/indeks/{}/{}/{}?page={}'''.format(category, tahun, bulan,
                                                                                               i + 1, page + 1)

                print(url)
                response = requests.get(url)
                html = response.text
                soup = BeautifulSoup(html, "html5lib")

                contents = soup.select('.articles--rows--item__details')

                for y in range(len(contents)):
                    title = contents[y].select_one('.articles--rows--item__title').text

                    if title[:6] != 'VIDEO:' and title[:5] != 'FOTO:' and title[:6] != 'FOTO :' and title[
                                                                                                    :5] != 'Top 3' and title[
                                                                                                                       :4] != 'Top3':
                        url_lokal = contents[y].select_one('.articles--rows--item__title > a')['href']
                        category = url.split('/')[3]
                        subCategory = contents[y].select_one('.articles--rows--item__category').text
                        title = contents[y].select_one('.articles--rows--item__title').text
                        description = contents[y].select_one('.articles--rows--item__summary').text
                        date = url.split('/')[7].split('?')[0] + '-' + url.split('/')[6] + '-' + url.split('/')[5]

                        data_json = {
                            "category": name_category,
                            "title": title,
                            "description": description,
                            "url": url_lokal,
                            "content": '',
                            "content_html": '',
                            "img": '',
                            "sub_category": subCategory,
                            "publishedAt": date,
                            "source": 'liputan6.com',
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

        return all_data

    def get_dataDaily(self, category=None, name_category=None, tahun=None, bulan=None, tanggal=None):
        all_data = []

        for i in tqdm(range(2), desc='Get Data Daily'):
            if bulan <= 9:
                if tanggal <= 9:
                    url = '''https://www.liputan6.com/{}/indeks/{}/0{}/0{}?page={}'''.format(category, tahun, bulan,
                                                                                             tanggal, i + 1)
                else:
                    url = '''https://www.liputan6.com/{}/indeks/{}/0{}/{}?page={}'''.format(category, tahun, bulan,
                                                                                            tanggal, i + 1)
            else:
                if tanggal <= 9:
                    url = '''https://www.liputan6.com/{}/indeks/{}/{}/0{}?page={}'''.format(category, tahun, bulan,
                                                                                            tanggal, i + 1)
                else:
                    url = '''https://www.liputan6.com/{}/indeks/{}/{}/{}?page={}'''.format(category, tahun, bulan,
                                                                                           tanggal, i + 1)

            print(url)
            response = requests.get(url)
            html = response.text
            soup = BeautifulSoup(html, "html5lib")

            contents = soup.select('.articles--rows--item__details')

            for y in range(len(contents)):
                title = contents[y].select_one('.articles--rows--item__title').text

                if title[:6] != 'VIDEO:' and title[:5] != 'FOTO:' and title[:6] != 'FOTO :' and title[
                                                                                                :5] != 'Top 3' and title[
                                                                                                                   :4] != 'Top3':
                    url_lokal = contents[y].select_one('.articles--rows--item__title > a')['href']
                    category = url.split('/')[3]
                    subCategory = contents[y].select_one('.articles--rows--item__category').text
                    title = contents[y].select_one('.articles--rows--item__title').text
                    description = contents[y].select_one('.articles--rows--item__summary').text
                    date = url.split('/')[7].split('?')[0] + '-' + url.split('/')[6] + '-' + url.split('/')[5]

                    data_json = {
                        "category": name_category,
                        "title": title,
                        "description": description,
                        "url": url_lokal,
                        "content": '',
                        "img": '',
                        "sub_category": subCategory,
                        "publishedAt": date,
                        "source": 'liputan6.com',
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

        return all_data

    def get_dataHarian(self, category=None, name_category=None, year=None, month=None, day=None):
        all_data = self.get_dataDaily(category, name_category, year, month, day)
        all_data = self.get_content2((all_data))
        all_data = self.clean_data(all_data)
        all_data = self.clean_content(all_data)

        return all_data

    def get_dataBulanan(self, category=None, name_category=None, year=None, month=None):
        all_data = self.get_dataMonthly(category, name_category, year, month)
        all_data = self.get_content2((all_data))
        all_data = self.clean_data(all_data)
        all_data = self.clean_content(all_data)

        return all_data

    def main(self):
        print(' ---- MENU SCRAPER ---- ')
        print('1. Bulanan ')
        print('2. Harian ')
        pilihan = eval(input('Pilihan : '))

        if pilihan == 1:
            category = input('Category : ')
            name_category = input('Name of Category : ')
            year = eval(input('Tahun : '))
            month = eval(input('Bulan : '))

            all_data = self.get_dataMonth(category, name_category, year, month)
            all_data = self.get_content2((all_data))
            all_data = self.clean_data(all_data)
            all_data = self.clean_content(all_data)

            # print(all_data2[0]['title'])

        elif pilihan == 2:
            category = input('Category : ')
            name_category = input('Name of Category : ')
            year = eval(input('Tahun : '))
            month = eval(input('Bulan : '))
            day = eval(input('Tanggal : '))

            all_data = self.get_dataDaily(category, name_category, year, month, day)
            all_data = self.get_content2((all_data))
            all_data = self.clean_data(all_data)
            all_data = self.clean_content(all_data)

            # print(all_data2[0])
        else:
            print('Pilihan Tidak Ada !!')

        return all_data

# if __name__== "__main__":
#
#     sl = Scraper_Liputan()
#     sl.main()