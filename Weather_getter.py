import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import cv2
import os
import sqlite3


class WeatherMaker:
    """"Класс получения прогноза погоды за определенный диапозон"""

    def __init__(self, date_1, date_2):
        self.url = 'https://darksky.net/details/55.7616,37.6095/'
        self.total_info = []
        self.dict_for_info = {}
        self.date_1 = date_1
        self.date_2 = date_2

    def get_ifo(self, url):
        info = requests.get(url)
        html_doc = BeautifulSoup(info.text, features='html.parser')
        list_for_temp = html_doc.find_all('span', {'class': 'temp'})
        list_for_state = html_doc.find_all('p', {'id': 'summary'})
        state = list_for_state[0].text
        temp = int(list_for_temp[1].text[:-1:])
        temp = int((temp - 32) * 5 / 9)
        return temp, state

    def get_weather(self):
        """Парсинг страницы яндекса"""
        t2 = timedelta(7)
        t1 = timedelta(1)
        date = self.date_1 - t2
        while date != self.date_2:
            date_to_url = str(date)[0:10:]
            new_date = datetime.strptime(date_to_url, "%Y-%m-%d").strftime("%d %B")
            new_url = f'{self.url}{date_to_url}'
            temp, state = self.get_ifo(url=new_url)
            dict_for_info = {'дата': new_date, 'погода': state, 'температура': temp}
            self.total_info.append(dict_for_info)
            date += t1


class ImageMaker:
    """Создает открытки и сохраняет их в папку saved"""

    def __init__(self, res):
        self.res = res
        self.image = cv2.imread(r'python_snippets/external_data/probe.jpg')

    def print_pic(self, pic, state):
        i = 0
        k = 0
        bg_dict = {'sunny': 5,
                   'snow': 5,
                   'rain': 3,
                   'cloud': 1}
        if state in bg_dict:
            for _ in range(50):
                if state == 'sunny':
                    self.image[:, 0 + i:50 + i] = (50 + k, 255 - k / 8, 238)
                elif state == 'snow':
                    self.image[:, 0 + i:50 + i] = (238, 255 - k / 8, 50 + k)
                elif state == 'rain':
                    self.image[:, 0 + i:50 + i] = (255, 80 + k, 80 + k)
                elif state == 'cloud':
                    self.image[:, 0 + i:50 + i] = (80 + k, 80 + k, 80 + k)
                i += 20
                k += bg_dict[state]
        else:
            self.image[:, 0 + i:50 + i] = (125, 255, 125)

        fwidth, fheight = pic.shape[:2]
        self.image[:fwidth, :fheight] = pic[:]

    def do_a_postcart(self):
        """Создает открытку"""
        date, state, temp = self.res['дата'], self.res['погода'].lower(), self.res['температура']
        pic_dict = {
            'clear': 'python_snippets/external_data/weather_img/sun.jpg',
            'cloud': 'python_snippets/external_data/weather_img/cloud.jpg',
            'overcast': 'python_snippets/external_data/weather_img/cloud.jpg',
            'rain': 'python_snippets/external_data/weather_img/rain.jpg',
            'snow': 'python_snippets/external_data/weather_img/sun.jpg'
        }
        if state in pic_dict:
            pic = cv2.imread(pic_dict[state])
        else:
            pic = cv2.imread('python_snippets/external_data/weather_img/sun.jpg')
            state = 'sunny'

        self.print_pic(pic, state)
        cv2.putText(img=self.image, text=f'{date}', org=(50, 170), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.2,
                    color=(0, 128, 255), thickness=2)
        cv2.putText(img=self.image, text=f'+{temp}', org=(350, 170), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.2,
                    color=(0, 128, 255), thickness=2)
        cv2.imwrite(f'saved/{date}.jpg', self.image)


class DatabaseUpdater:
    """Класс по созданию и обновлению базы, а также получения из нее всей информации."""

    def create_db(self, elem):
        date = elem['дата']
        state = elem['погода']
        temp = elem['температура']
        with sqlite3.connect('weather.db') as conn:
            cur = conn.cursor()
            cur.execute(f"INSERT INTO weather VALUES ('{date}', '{state}', '+{temp}')")
            conn.commit()

    def get_data(self):
        with sqlite3.connect('weather.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM weather;")
            data = cur.fetchall()
            return data


class WeatherForecaster:
    def __init__(self, num, date_1, date_2):
        self.num = num
        self.date1 = datetime.strptime(date_1, "%Y-%m-%d")
        self.date2 = datetime.strptime(date_2, "%Y-%m-%d")
        self.res = []

    def get_info(self):
        weather_info = WeatherMaker(self.date1, self.date2)
        weather_info.get_weather()
        self.res = weather_info.total_info

    def do_stuff(self):
        new_date = (datetime.strptime(str(self.date2)[0:10:], "%Y-%m-%d").strftime("%d %B"),)
        base = DatabaseUpdater()
        with sqlite3.connect('weather.db') as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS weather (date TEXT PRIMARY KEY, state TEXT, temp TEXT)")
            conn.commit()
            cur.execute("SELECT date FROM weather;")
            dates = cur.fetchall()

        if not (new_date in dates):
            self.get_info()
        else:
            data = base.get_data()
            for date, state, temp in data:
                self.res.append({'дата': date, 'погода': state, 'температура': temp})
                if date == new_date[0]:
                    break
        if self.num == '1':
            for elem in self.res:
                try:
                    base.create_db(elem)
                except Exception:
                    pass

        elif self.num == '2':
            data = base.get_data()
            for date, state, temp in data:
                print(date + ',', state + ',', temp)

        elif self.num == '3':
            os.makedirs('saved', exist_ok=True)
            for elem in self.res:
                imager = ImageMaker(res=elem)
                imager.do_a_postcart()

        elif self.num == '4':
            for elem in self.res:
                print(f'{elem["дата"]}, {elem["погода"]}, {elem["температура"]}')
