from bs4 import BeautifulSoup
import requests
from matplotlib import font_manager, rc
import matplotlib.pyplot as plt
import os
from myProject03.settings import STATIC_DIR


def melon_crawling(datas):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }

    url = 'https://www.melon.com/chart/week/index.htm'
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.content, 'html.parser')

    tbody = soup.select_one('#frm > div > table > tbody')
    trs = tbody.select('tr')
    for chart in trs[:20]:
        tds = chart.select('td')
        ranking = tds[1].select_one('span.rank').text
        title = tds[5].select_one('div.ellipsis.rank01 > span > a').text
        singer = tds[5].select_one('div.ellipsis.rank02 > a').text
        album = tds[6].select_one('div.ellipsis.rank03 > a').text

        tmp = dict()
        tmp['ranking'] = ranking
        tmp['title'] = title
        tmp['singer'] = singer
        tmp['album'] = album

        datas.append(tmp)


def weather_crawling(last_date, weather):
    url = 'https://www.weather.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=108'
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'lxml')

    for i in soup.find_all('location'):
        weather[i.find('city').text] = []
        for j in i.find_all('data'):
            temp = []
            if(len(last_date) == 0) or (j.find('tmef').text > last_date[0]['tmef']):
                temp.append(j.find('tmef').text)
                temp.append(j.find('wf').text)
                temp.append(j.find('tmn').text)
                temp.append(j.find('tmx').text)
                weather[i.find('city').string].append(temp)


def weather_make_chart(result, wfs, dcounts):
    font_location = "c:/Windows/fonts/malgun.ttf"
    font_name = font_manager.FontProperties(fname=font_location).get_name()
    rc('font', family=font_name)

    high = []
    low = []
    xdata = []

    for row in result.values_list():
        high.append(row[5])
        low.append(row[4])
        xdata.append(row[2].split('-')[2])

    plt.cla()
    plt.figure(figsize=(10, 6))
    plt.plot(xdata, low, label="최저기온")
    plt.plot(xdata, high, label="최고기온")
    plt.xticks(rotation=45)
    plt.legend()
    plt.savefig(os.path.join(STATIC_DIR, 'images/weather_plot.png'), dpi=300)
    
    plt.cla()
    plt.bar(wfs, dcounts)
    plt.savefig(os.path.join(STATIC_DIR, 'images/weather_bar.png'), dpi=300)
    
    plt.cla()
    plt.pie(dcounts, labels=wfs, autopct='%.1f%%')
    plt.savefig(os.path.join(STATIC_DIR, 'images/weather_pie.png'), dpi=300)
    
    image_dic = {
        'plot': 'weather_plot.png',
        'bar': 'weather_bar.png',
        'pie': 'weather_pie.png'
    }
    return image_dic
