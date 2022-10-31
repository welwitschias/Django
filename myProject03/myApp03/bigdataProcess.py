import os
import re
from collections import Counter

import folium
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from konlpy.tag import Okt
from matplotlib import font_manager, rc
from myProject03.settings import STATIC_DIR, TEMPLATE_DIR
from pandas import DataFrame
from wordcloud import WordCloud


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


def map():
    ex = {'경도': [127.061026, 127.047883, 127.899220, 128.980455, 127.104071, 127.102490, 127.088387, 126.809957, 127.010861, 126.836078, 127.014217, 126.886859, 127.031702, 126.880898, 127.028726, 126.897710, 126.910288, 127.043189, 127.071184, 127.076812, 127.045022, 126.982419, 126.840285, 127.115873, 126.885320, 127.078464, 127.057100, 127.020945, 129.068324, 129.059574, 126.927655, 127.034302, 129.106330, 126.980242, 126.945099, 129.034599, 127.054649, 127.019556, 127.053198, 127.031005, 127.058560, 127.078519, 127.056141, 129.034605, 126.888485, 129.070117, 127.057746, 126.929288, 127.054163, 129.060972],
          '위도': [37.493922, 37.505675, 37.471711, 35.159774, 37.500249, 37.515149, 37.549245, 37.562013, 37.552153, 37.538927, 37.492388, 37.480390, 37.588485, 37.504067, 37.608392, 37.503693, 37.579029, 37.580073, 37.552103, 37.545461, 37.580196, 37.562274, 37.535419, 37.527477, 37.526139, 37.648247, 37.512939, 37.517574, 35.202902, 35.144776, 37.499229, 35.150069, 35.141176, 37.479403, 37.512569, 35.123196, 37.546718, 37.553668, 37.488742, 37.493653, 37.498462, 37.556602, 37.544180, 35.111532, 37.508058, 35.085777, 37.546103, 37.483899, 37.489299, 35.143421],
          '구분': ['음식', '음식', '음식', '음식', '생활서비스', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '소매', '음식', '음식', '음식', '음식', '소매', '음식', '소매', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '음식', '소매', '음식', '음식', '의료', '음식', '음식', '음식', '소매', '음식', '음식', '음식', '음식', '음식', '음식', '음식']}
    ex = DataFrame(ex)

    latitude_mean = ex['위도'].mean()
    longitude_mean = ex['경도'].mean()

    # 지도 띄우기
    map = folium.Map([latitude_mean, longitude_mean], zoom_start=9)

    for i in ex.index:
        sub_lat = ex.loc[i, '위도']
        sub_long = ex.loc[i, '경도']
        title = ex.loc[i, '구분']
        folium.Marker([sub_lat, sub_long], tooltip=title).add_to(map)

    map.save(os.path.join(TEMPLATE_DIR, 'bigdata/maptest.html'))


def make_wordcloud(data):
    message = ''
    for i in data:
        if 'message' in i.keys():
            # 문자와 숫자가 아닌 것은 공백으로 처리
            message = message + re.sub(r'[^\w]+', ' ', i['message'])+''

    # 명사만 추출하기
    nlp = Okt()
    message_Noun = nlp.nouns(message)
    count = Counter(message_Noun)

    # 글자수가 2개 이상인 단어 80개 추출
    word_count = {}
    for tag, counts in count.most_common(80):
        if(len(str(tag))) > 1:
            word_count[tag] = counts

    font_path = 'c:/Windows/Fonts/malgun.ttf'

    # wordcloud 작성
    wc = WordCloud(font_path, background_color='ivory',
                   width=800, height=600)
    cloud = wc.generate_from_frequencies(word_count)
    plt.figure(figsize=(8, 8))
    plt.imshow(cloud)
    plt.axis('off')
    cloud.to_file('./static/images/k_wordcloud.png')


def movie_crawling(datas):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }

    url = 'https://movie.daum.net/ranking/reservation'
    response = requests.get(url, headers=header)
    soup = BeautifulSoup(response.content, 'html.parser')

    movieList = soup.find('ol', class_="list_movieranking")
    rankcont = movieList.find_all('div', class_="thumb_cont")

    movieRanking = 0
    for i in rankcont[:20]:
        movieRanking += 1
        movieTitle = i.find('a', class_="link_txt").get_text()
        movieGrade = i.find('span', class_="txt_grade").get_text()
        movieReserv = i.find('span', class_="txt_num").get_text()

        tmp = dict()
        tmp['movieRanking'] = movieRanking
        tmp['movieTitle'] = movieTitle
        tmp['movieGrade'] = movieGrade
        tmp['movieReserv'] = movieReserv

        datas.append(tmp)

    movie_dict = {
        '평점 9.0 이상': 0,
        '평점 8.0 이상': 0,
        '평점 7.0 이상': 0,
        '평점 7.0 미만': 0
    }

    for item in datas:
        grade = float(item['movieGrade'])

        if grade >= 9.0:
            movie_dict['평점 9.0 이상'] += 1
        elif grade >= 8.0:
            movie_dict['평점 8.0 이상'] += 1
        elif grade >= 7.0:
            movie_dict['평점 7.0 이상'] += 1
        elif grade >= 0.0:
            movie_dict['평점 7.0 미만'] += 1

    font_location = "c:/Windows/fonts/malgun.ttf"
    font_name = font_manager.FontProperties(fname=font_location).get_name()
    rc('font', family=font_name)

    figure = plt.figure()
    axes = figure.add_subplot(111)
    axes.pie(movie_dict.values(), labels=movie_dict.keys(), autopct='%.1f%%')
    plt.savefig(os.path.join(STATIC_DIR, 'images/movie_pie.png'), dpi=300)
