import json
import spacy
import id_aldo
import requests
import datetime
from spacy import displacy
from bs4 import BeautifulSoup
from tqdm import tqdm, tqdm_notebook
from textacy.preprocess import preprocess_text

nlp = id_aldo.load()

now = datetime.date.today()

category = ['tekno', 'entertainment', 'otomotif', 'bola']

def ner_text(text=None):
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

def get_content(url=None):
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
    p = ner_text(p)

    data_json = {
        "img": temp_img,
        "content": p,
    }

    return data_json

def get_content_fix(all_data):
    for i in tqdm(range(len(all_data))):
        try:
            temp = get_content(all_data[i]['url'])
            all_data[i]['content'] = temp['content']
            all_data[i]['img'] = temp['img']
        except:
            pass

    return all_data

def clean_data(all_data):
    all_data2 = []
    for ad in all_data:
        if ad['content'] != '': all_data2.append(ad)

    return all_data2


def get_dataDaily(category, now):
    all_data = []
    for cat in category:
        url = '''https://{}.kompas.com/search/{}-{}-{}'''.format(cat, now.year, now.month, now.day)
        response = requests.get(url).text
        soup = BeautifulSoup(response, "html5lib")
        count_page = soup.select('.paging__wrap.clearfix > .paging__item')

        if count_page == []:
            url_lokal = url
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
                        "category": cat,
                        "title": temp_title,
                        "description": '',
                        "url": temp_url,
                        "sub_category": temp_category,
                        "publishedAt": temp_date,
                        "img": '',
                        "content": '',
                        "status_data": 'No'
                    }

                    all_data.append(json.loads(json.dumps(data_json)))

                except:
                    pass
        else:
            total_page = int(count_page[len(count_page) - 1].select('.paging__link')[0]['data-ci-pagination-page'])

            for y in range(total_page):
                try:
                    url_lokal = url + '/' + '{}'.format(y + 1)
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
                                "category": cat,
                                "title": temp_title,
                                "description": '',
                                "url": temp_url,
                                "sub_category": temp_category,
                                "publishedAt": temp_date,
                                "img": '',
                                "content": '',
                                "status_data": 'No'
                            }

                            all_data.append(json.loads(json.dumps(data_json)))

                        except:
                            pass
                except:
                    pass

    return all_data

x = get_dataDaily(category, now)

print(x[0])