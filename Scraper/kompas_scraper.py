import spacy
import id_aldo
import requests
import datetime
from spacy import displacy
from bs4 import BeautifulSoup
from tqdm import tqdm, tqdm_notebook
from textacy.preprocess import preprocess_text

nlp = id_aldo.load()

class Scraper_Kompas():

    def __init__(self):
        self

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
        response = requests.get(url, timeout=3).text
        soup = BeautifulSoup(response, "html5lib")

        contents = soup.select_one('.photo > img')
        contents2 = soup.select('.read__content > p')

        temp_img = contents['src']

        data = []
        for i in range(len(contents2)):
            if contents2[i].text != '':
                if (contents2[i].text[:9] != 'Baca juga' and contents2[i].text[:5] != 'Baca:') \
                        and (contents2[i].text[:15] != 'We are thrilled') and (contents2[i].text[:6] != 'Flinke'):
                    data.append(contents2[i].text)

        p = ''.join(data)
        p = preprocess_text(p, fix_unicode=True)
        p = self.ner_text(p)

        data_json = {
            "img": temp_img,
            "content": p,
        }

        return data_json

    def get_content_fix(self, all_data=None):
        for i in tqdm(range(len(all_data))):
            try:
                temp = self.get_content(all_data[i]['url'])
                all_data[i]['content'] = temp['content']
                all_data[i]['img'] = temp['img']
            except:
                pass

        return all_data

    def clean_data(self, all_data=None):
        all_data2 = []
        for ad in all_data:
            if ad['content'] != '': all_data2.append(ad)

        return all_data2


    def get_dataMonth(self, global_category=None, name_category=None, tahun=None, bulan=None):
        all_data = []
        for tanggal in tqdm(range(31)):
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

                    for content in (contents):
                        try:
                            temp_category = content.select_one('.article__subtitle').text.strip()
                            temp_url = content.select_one('.article__link')['href']
                            temp_title = content.select_one('.article__link').text.strip()
                            temp_date = content.select_one('.article__date').text.replace(',', '').split()[0]
                            temp_date = datetime.datetime.strptime(temp_date, "%d/%m/%Y").strftime("%Y-%m-%d")

                            data_json = {
                                "category": name_category,
                                "title": temp_title,
                                "description": '',
                                "url": temp_url,
                                "content": '',
                                "img": '',
                                "sub_category": temp_category,
                                "publishedAt": temp_date,
                                "source" : 'kompas.com',
                                "clean_content": ''
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

                            for content in (contents):
                                try:
                                    temp_category = content.select_one('.article__subtitle').text.strip()
                                    temp_url = content.select_one('.article__link')['href']
                                    temp_title = content.select_one('.article__link').text.strip()
                                    temp_date = content.select_one('.article__date').text.replace(',', '').split()[0]
                                    temp_date = datetime.datetime.strptime(temp_date, "%d/%m/%Y").strftime("%Y-%m-%d")

                                    data_json = {
                                        "category": name_category,
                                        "title": temp_title,
                                        "description": '',
                                        "url": temp_url,
                                        "content": '',
                                        "img": '',
                                        "sub_category": temp_category,
                                        "publishedAt": temp_date,
                                        "source" : 'kompas.com',
                                        "clean_content": ''
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

            for content in (contents):
                try:
                    temp_category = content.select_one('.article__subtitle').text.strip()
                    temp_url = content.select_one('.article__link')['href']
                    temp_title = content.select_one('.article__link').text.strip()
                    temp_date = content.select_one('.article__date').text.replace(',', '').split()[0]
                    temp_date = datetime.datetime.strptime(temp_date, "%d/%m/%Y").strftime("%Y-%m-%d")

                    data_json = {
                        "category": name_category,
                        "title": temp_title,
                        "description": '',
                        "url": temp_url,
                        "content": '',
                        "img": '',
                        "sub_category": temp_category,
                        "publishedAt": temp_date,
                        "source" : 'kompas.com',
                        "clean_content": ''
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

                    for content in (contents):
                        try:
                            temp_category = content.select_one('.article__subtitle').text.strip()
                            temp_url = content.select_one('.article__link')['href']
                            temp_title = content.select_one('.article__link').text.strip()
                            temp_date = content.select_one('.article__date').text.replace(',', '').split()[0]
                            temp_date = datetime.datetime.strptime(temp_date, "%d/%m/%Y").strftime("%Y-%m-%d")

                            data_json = {
                                "category": name_category,
                                "title": temp_title,
                                "description": '',
                                "url": temp_url,
                                "content": '',
                                "img": '',
                                "sub_category": temp_category,
                                "publishedAt": temp_date,
                                "source": 'kompas.com',
                                "clean_content": ''
                            }

                            all_data.append(data_json)

                        except:
                            pass
                except:
                    pass

        return all_data




    def main(self):
        print(' ---- MENU SCRAPER ---- ')
        print('1. Bulanan ')
        print('2. Harian ')
        pilihan = eval(input('Pilihan : '))

        if pilihan == 1:
            category = input('Category : ')
            year = eval(input('Tahun : '))
            month = eval(input('Bulan : '))

            all_data = self.get_dataMonth(category, year, month)
            temp_data = self.get_content_fix((all_data))

            all_data2 = self.clean_data(temp_data)

        elif pilihan == 2:
            category = input('Category : ')
            year = eval(input('Tahun : '))
            month = eval(input('Bulan : '))
            day = eval(input('Tanggal : '))

            all_data = self.get_dataDaily(category, year, month, day)
            temp_data = self.get_content_fix((all_data))

            all_data2 = self.clean_data(temp_data)

        else:
            print('Pilihan Tidak Ada !!')


# if __name__== "__main__":
#     main()
