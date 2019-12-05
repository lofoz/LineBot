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
    target_url = 'https://movies.yahoo.com.tw/'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    movies_group = []
    for index, datas in enumerate(soup.select('div._slickcontent')):
        # 可能可以改成 push 的方式
        if index == 10:
            break
        data = datas.find('h2')
        movie_title = data.find('a').text
        date = datas.find('h3').text
        expect_find = datas.find('div', {'class':'percent'})
        if expect_find == None:
            type = '星級'
            expect = datas.find('div', {'class':'star_num count'}).text
        else:
            type = '期待度'
            expect = expect_find.find('span').text
        link = data.find('a')['href']
        img_link = datas.find('img')['src']
        #img_link = upload_photo(img_link)
        movie_data = CarouselColumn(
            thumbnail_image_url = img_link,
            title = movie_title,
            text = date,
            actions = [
                URIAction(label = 'Detail', uri = link),
                MessageAction(label = 'OK', text = '米')
            ]
        )
        movies_group.append(movie_data)

    carousel_template = CarouselTemplate(columns = movies_group)
    template_message = TemplateSendMessage(alt_text = 'Carousel alt text', template = carousel_template)
    send_template_message(reply_token, template_message)
        #movies_type.append(type)
        #movies_expect.append(expect)
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
            PostbackAction(label = '預告片榜', data = '預告片榜')
        ])
    template_message = TemplateSendMessage(alt_text = 'Buttons alt text', template = buttons_template)
    send_template_message(reply_token, template_message)
    return True

def show_hot_movies_tw(reply_token):
    requests.packages.urllib3.disable_warnings()
    target_url = 'https://movies.yahoo.com.tw/'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    link = []
    movies_title = []
    img_link = []
    carousel_group = []
    # content = ""
    # 改 list 1,2,3
    for index, datas in enumerate(soup.select('div#list1 ul a')):
        if index == 10:
            break
        # 找圖片
        movie_url = datas['href']
        movie_rs = requests.session()
        movie_res = movie_rs.get(movie_url, verify=False)
        movie_res.encoding = 'utf-8'
        movie_soup = BeautifulSoup(movie_res.text, 'html.parser')
        movie_img_data = movie_soup.select_one('div .movie_intro_foto img')
        img_link.append(movie_img_data['src'])
        link.append(datas['href'])
        movies_title.append(datas.li.span.text)
    # 改 list 1,2,3
    for index, datas in enumerate(soup.select('div#list1 ul .unclick')):
        if index == 10:
            break
        link.insert(int(datas.find('div', {'class': 'num'}).text) - 1, "No URL")
        img_link.insert(int(datas.find('div', {'class': 'num'}).text) - 1, "No URL")
        movies_title.insert(int(datas.find('div', {'class': 'num'}).text) - 1, datas.span.text)
    x = ['title', 'img_link', 'link']
    movies_group = []
    movies_group.append(movies_title)
    movies_group.append(img_link)
    movies_group.append(link)
    movies_dic = dict(zip(x, movies_group))
    for i in range(10):
        if (movies_dic['link'][i] != 'No URL'):
            carousel_data = CarouselColumn(
                thumbnail_image_url=movies_dic['img_link'][i],
                title=movies_dic['title'][i],
                text = '123',
                actions=[
                    URIAction(label='Detail', uri=movies_dic['link'][i]),
                    MessageAction(label='OK', text='米')
                ]
            )
        else:
            carousel_data = CarouselColumn(
                thumbnail_image_url='https://movies.tw.campaign.yahoo.net/i/o/production/movies/August2019/vpVOFf6g6g3WiSd1qFTN-2764x4096.jpeg',
                title=movies_dic['title'][i],
                text = '123',
                actions=[
                    URIAction(label='Detail', uri='https://movies.tw.campaign.yahoo.net/i/o/production/movies/August2019/vpVOFf6g6g3WiSd1qFTN-2764x4096.jpeg'),
                    MessageAction(label='OK', text='米')
                ]
            )
        carousel_group.append(carousel_data)
        # print(movies_dic['link'][i])
        # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
    carousel_template = CarouselTemplate(columns=carousel_group)
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
    send_template_message(reply_token, template_message)
    return True

def show_hot_movies_us(reply_token):
    requests.packages.urllib3.disable_warnings()
    target_url = 'https://movies.yahoo.com.tw/'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    link = []
    movies_title = []
    img_link = []
    carousel_group = []
    # content = ""
    # 改 list 1,2,3
    for index, datas in enumerate(soup.select('div#list2 ul a')):
        if index == 10:
            break
        # 找圖片
        movie_url = datas['href']
        movie_rs = requests.session()
        movie_res = movie_rs.get(movie_url, verify=False)
        movie_res.encoding = 'utf-8'
        movie_soup = BeautifulSoup(movie_res.text, 'html.parser')
        movie_img_data = movie_soup.select_one('div .movie_intro_foto img')
        img_link.append(movie_img_data['src'])
        link.append(datas['href'])
        movies_title.append(datas.li.span.text)
    # 改 list 1,2,3
    for index, datas in enumerate(soup.select('div#list2 ul .unclick')):
        if index == 10:
            break
        link.insert(int(datas.find('div', {'class': 'num'}).text) - 1, "No URL")
        img_link.insert(int(datas.find('div', {'class': 'num'}).text) - 1, "No URL")
        movies_title.insert(int(datas.find('div', {'class': 'num'}).text) - 1, datas.span.text)
    x = ['title', 'img_link', 'link']
    movies_group = []
    movies_group.append(movies_title)
    movies_group.append(img_link)
    movies_group.append(link)
    movies_dic = dict(zip(x, movies_group))
    for i in range(10):
        if (movies_dic['link'][i] != 'No URL'):
            carousel_data = CarouselColumn(
                thumbnail_image_url=movies_dic['img_link'][i],
                title=movies_dic['title'][i],
                text='123',
                actions=[
                    URIAction(label='Detail', uri=movies_dic['link'][i]),
                    MessageAction(label='OK', text='米')
                ]
            )
        else:
            carousel_data = CarouselColumn(
                thumbnail_image_url='https://movies.tw.campaign.yahoo.net/i/o/production/movies/August2019/vpVOFf6g6g3WiSd1qFTN-2764x4096.jpeg',
                title=movies_dic['title'][i],
                text='123',
                actions=[
                    URIAction(label='Detail',
                              uri='https://movies.yahoo.com.tw/movieinfo_main/%E5%86%B0%E9%9B%AA%E5%A5%87%E7%B7%A32-frozen-2-9597'),
                    MessageAction(label='OK', text='米')
                ]
            )
        carousel_group.append(carousel_data)
        # print(movies_dic['link'][i])
        # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
    carousel_template = CarouselTemplate(columns=carousel_group)
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
    send_template_message(reply_token, template_message)
    return True

def show_hot_movies_un(reply_token):
    requests.packages.urllib3.disable_warnings()
    target_url = 'https://movies.yahoo.com.tw/'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    link = []
    movies_title = []
    img_link = []
    carousel_group = []
    # content = ""
    # 改 list 1,2,3
    for index, datas in enumerate(soup.select('div#list3 ul a')):
        if index == 10:
            break
        # 找圖片
        movie_url = datas['href']
        movie_rs = requests.session()
        movie_res = movie_rs.get(movie_url, verify=False)
        movie_res.encoding = 'utf-8'
        movie_soup = BeautifulSoup(movie_res.text, 'html.parser')
        movie_img_data = movie_soup.select_one('div .movie_intro_foto img')
        img_link.append(movie_img_data['src'])
        link.append(datas['href'])
        movies_title.append(datas.li.span.text)
    # 改 list 1,2,3
    for index, datas in enumerate(soup.select('div#list3 ul .unclick')):
        if index == 10:
            break
        link.insert(int(datas.find('div', {'class': 'num'}).text) - 1, "No URL")
        img_link.insert(int(datas.find('div', {'class': 'num'}).text) - 1, "No URL")
        movies_title.insert(int(datas.find('div', {'class': 'num'}).text) - 1, datas.span.text)
    x = ['title', 'img_link', 'link']
    movies_group = []
    movies_group.append(movies_title)
    movies_group.append(img_link)
    movies_group.append(link)
    movies_dic = dict(zip(x, movies_group))
    for i in range(10):
        if (movies_dic['link'][i] != 'No URL'):
            carousel_data = CarouselColumn(
                thumbnail_image_url=movies_dic['img_link'][i],
                title=movies_dic['title'][i],
                text='123',
                actions=[
                    URIAction(label='Detail', uri=movies_dic['link'][i]),
                    MessageAction(label='OK', text='米')
                ]
            )
        else:
            carousel_data = CarouselColumn(
                thumbnail_image_url='https://movies.tw.campaign.yahoo.net/i/o/production/movies/August2019/vpVOFf6g6g3WiSd1qFTN-2764x4096.jpeg',
                title=movies_dic['title'][i],
                text='123',
                actions=[
                    URIAction(label='Detail',
                              uri='https://movies.tw.campaign.yahoo.net/i/o/production/movies/August2019/vpVOFf6g6g3WiSd1qFTN-2764x4096.jpeg'),
                    MessageAction(label='OK', text='米')
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
