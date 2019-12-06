from __future__ import unicode_literals
import os
from linebot import LineBotApi
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)
from imgurpython import ImgurClient
import requests
from bs4 import BeautifulSoup


channel_access_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")


def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))
    return True

def send_template_message(reply_token, template):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, template)
    return True

def SwitchMenuTo(MenuName, event):
    line_bot_api = LineBotApi(channel_access_token)
    rich_menu_list = line_bot_api.get_rich_menu_list()
    for rich_menu in rich_menu_list:
        if rich_menu.name == MenuName:
            #print(rich_menu.rich_menu_id)
            #print(event.source.user_id)
            line_bot_api.link_rich_menu_to_user(event.source.user_id, rich_menu.rich_menu_id)
            return True
    return False

def show_new_movies(reply_token):
    requests.packages.urllib3.disable_warnings()
    # 本周新片
    target_url = 'https://movies.yahoo.com.tw/movie_thisweek.html'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    link = []
    movies_title = []
    date = []
    # 預告片
    movies_pre = []
    # 電影簡介
    movies_text = []
    # 評價
    movies_star = []
    img_link = []
    carousel_group = []
    # content = ""
    for index, datas in enumerate(soup.select('ul.release_list li')):
        # index-1 -> 找的數量
        if index == 11:
            break
        img_link.append(datas.find('img')['src'])
        movie_info_u = datas.find('div', 'release_info_text')
        movie_info_l = datas.find('div', 'release_btn')
        movie_info = movie_info_u.find('div', 'release_movie_name')
        link.append(movie_info.find('a')['href'])
        movies_title.append(movie_info.find('a').text.lstrip())
        movies_star.append(movie_info.find('dl', 'levelbox').dt.span.text)
        date.append(movie_info_u.find('div', 'release_movie_time').text)
        movies_text.append(movie_info_u.find('div', 'release_text').span.text.lstrip())
        movies_pre.append(movie_info_l.find_all('a')[1]['href'])

    # 製作line 回復訊息
    x = ['title', 'img_link', 'link', 'movies_pre', 'date', 'movies_star', 'movies_text']
    movies_group = []
    movies_group.append(movies_title)
    movies_group.append(img_link)
    movies_group.append(link)
    movies_group.append(movies_pre)
    movies_group.append(date)
    movies_group.append(movies_star)
    movies_group.append(movies_text)
    movies_dic = dict(zip(x, movies_group))
    for i in range(10):
        detail = movies_dic['date'][i] + '\n' + '網友期待度 ： ' + movies_dic['movies_star'][i] + '\n' + '劇情介紹 ： ' + movies_dic['movies_text'][i]
        carousel_data = CarouselColumn(
            thumbnail_image_url=movies_dic['img_link'][i],
            title=movies_dic['title'][i],
            text=detail[0:60],
            actions=[
                URIAction(label='詳細內容', uri=movies_dic['link'][i]),
                URIAction(label='預告片', uri=movies_dic['movies_pre'][i]),
                MessageAction(label='加入最愛', text='米')
            ]
        )
        carousel_group.append(carousel_data)
        # print(movies_dic['link'][i])
        # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
    carousel_template = CarouselTemplate(columns=carousel_group)
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
    send_template_message(reply_token, template_message)
    return True

def show_movie_leaderboard(reply_token):
    requests.packages.urllib3.disable_warnings()
    target_url = 'https://movies.yahoo.com.tw/'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    # 改 list 1,2,3
    data = soup.select_one('div #list1 .ranking_top_info_img_r img')
    img_link = data['src']
    buttons_template = ButtonsTemplate(
        image_aspect_ratio = 'square',
        image_size = 'cover',
        thumbnail_image_url = img_link,
        title = '排行榜',
        text = '請按下方選項',
        actions = [
            PostbackAction(label = '台北票房榜', data = '台北票房榜'),
            PostbackAction(label = '全美票房榜', data = '全美票房榜'),
            PostbackAction(label = '年度票房榜', data = '年度票房榜')
        ])
    template_message = TemplateSendMessage(alt_text = 'Buttons alt text', template = buttons_template)
    send_template_message(reply_token, template_message)
    return True

def show_hot_movies(reply_token, chart):
    requests.packages.urllib3.disable_warnings()
    # 年度票房 or 全美票房 or 台北票房
    if chart == '台北票房榜':
        target_url = 'https://movies.yahoo.com.tw/chart.html'
    elif chart == '全美票房榜':
        target_url = 'https://movies.yahoo.com.tw/chart.html?cate=us'
    elif chart == '年度票房榜':
        target_url = 'https://movies.yahoo.com.tw/chart.html?cate=year'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    link = []
    movies_title = []
    date = []
    # 預告片
    movies_pre = []
    # 評價
    movies_star = []
    img_link = []
    carousel_group = []
    # content = ""
    # 改 list 1,2,3
    for index, datas in enumerate(soup.select('div.rank_list.table.rankstyle1 div.tr')):
        if index == 0:
            continue
        # index-1 -> 找的數量
        if index == 8:
            break
        movie_info = datas.find_all('div')
        non = movie_info[3].find('a')
        if non != None:
            link.append(non['href'])
            # 找圖片
            movie_url = link[index - 1]
            movie_rs = requests.session()
            movie_res = movie_rs.get(movie_url, verify=False)
            movie_res.encoding = 'utf-8'
            movie_soup = BeautifulSoup(movie_res.text, 'html.parser')
            movie_img_data = movie_soup.select_one('div .movie_intro_foto img')
            img_link.append(movie_img_data['src'])
        else:
            link.append('')
            img_link.append('')
        if index == 1:
            movies_title.append(movie_info[3].find('h2').text)
            date.append(movie_info[4].text)
            non = movie_info[5].find('a')
            # 找預告片
            if non != None:
                movies_pre.append(non['href'])
            else:
                movies_pre.append('')
            non = movie_info[6].find('h6')
            # 找評價星星
            if non != None:
                movies_star.append(non.text)
            else:
                movies_star.append('')
        else:
            movies_title.append(movie_info[3].find('div', 'rank_txt').text)
            date.append(movie_info[5].text)
            non = movie_info[6].find('a')
            # 找預告片
            if non != None:
                movies_pre.append(non['href'])
            else:
                movies_pre.append('')
            non = movie_info[7].find('h6')
            # 找評價星星
            if non != None:
                movies_star.append(non.text)
            else:
                movies_star.append('')
    # 製作line 回復訊息
    x = ['title', 'img_link', 'link', 'movies_pre', 'date', 'movies_star']
    movies_group = []
    movies_group.append(movies_title)
    movies_group.append(img_link)
    movies_group.append(link)
    movies_group.append(movies_pre)
    movies_group.append(date)
    movies_group.append(movies_star)
    movies_dic = dict(zip(x, movies_group))
    for i in range(7):
        if (movies_dic['link'][i] != ''):
            carousel_data = CarouselColumn(
                thumbnail_image_url=movies_dic['img_link'][i],
                title=movies_dic['title'][i],
                text='上映日期 ： '+movies_dic['date'][i]+'\n'+'網友滿意度 ： '+str((float(movies_dic['movies_star'][i]))*20),
                actions=[
                    URIAction(label='詳細內容', uri=movies_dic['link'][i]),
                    URIAction(label='預告片', uri=movies_dic['movies_pre'][i]),
                    MessageAction(label='加入最愛', text='米')
                ]
            )
        else:
            carousel_data = CarouselColumn(
                thumbnail_image_url='https://movies.tw.campaign.yahoo.net/i/o/production/movies/August2019/vpVOFf6g6g3WiSd1qFTN-2764x4096.jpeg',
                title=movies_dic['title'][i],
                text='上映日期：'+movies_dic['date'][i],
                actions=[
                    URIAction(label='詳細內容',
                              uri='https://movies.tw.campaign.yahoo.net/i/o/production/movies/August2019/vpVOFf6g6g3WiSd1qFTN-2764x4096.jpeg'),
                    URIAction(label='預告片',
                              uri='https://movies.tw.campaign.yahoo.net/i/o/production/movies/August2019/vpVOFf6g6g3WiSd1qFTN-2764x4096.jpeg'),
                    MessageAction(label='加入最愛', text='米')
                ]
            )
        carousel_group.append(carousel_data)
        # print(movies_dic['link'][i])
        # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
    carousel_template = CarouselTemplate(columns=carousel_group)
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
    send_template_message(reply_token, template_message)
    return True

def upload_photo(image_url):
    client_id = '08dd33b004aeb70'
    client_secret = 'df0e8f73218d6046b49cf3d481f898ff658868fa'
    access_token = '714846b6f07dddaea1b9144a0b5fdc1e49c2cc93'
    refresh_token = '714846b6f07dddaea1b9144a0b5fdc1e49c2cc93'
    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
    album = None # You can also enter an album ID here
    config = {
        'album': album,
    }
    print("Uploading image... ")
    image = client.upload_from_url(image_url, config=config, anon=False)
    print("Done")
    return image['link']


"""
def send_image_url(id, img_url):
    pass

def send_button_message(id, text, buttons):
    pass
"""
