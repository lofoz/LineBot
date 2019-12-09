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
import  random

favorite_movies = {}
favorite_animates = {}
win_game = {}
channel_access_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

def push_text_message(event, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.push_message(event.source.user_id, TextSendMessage(text=text))
    return True

def push_template_message(event, template):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.push_message(event.source.user_id, template)
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

def show_new_movies(event):
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
        # index -> 找的數量
        if index == 10:
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
    for i in range(len(movies_title)):
        detail = movies_dic['date'][i] + '\n' + '網友期待度 ： ' + movies_dic['movies_star'][i] + '\n' + '劇情介紹 ： ' + movies_dic['movies_text'][i]
        carousel_data = CarouselColumn(
            thumbnail_image_url=movies_dic['img_link'][i],
            title=movies_dic['title'][i][0:40],
            text=detail[0:60],
            actions=[
                URIAction(label='詳細內容', uri=movies_dic['link'][i]),
                URIAction(label='預告片', uri=movies_dic['movies_pre'][i]),
                PostbackAction(label='加入最愛', data='movie,' + movies_dic['link'][i])
            ]
        )
        carousel_group.append(carousel_data)
        # print(movies_dic['link'][i])
        # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
    carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
    push_template_message(event, template_message)
    return True

def show_movie_leaderboard(event):
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
            PostbackAction(label = '年度票房榜', data = '年度票房榜'),
            PostbackAction(label='預告片榜', data='預告片榜')
        ])
    template_message = TemplateSendMessage(alt_text = 'Buttons alt text', template = buttons_template)
    push_template_message(event, template_message)
    return True

def show_hot_movies(event, chart):
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
    # 電影連結
    link = []
    # 電影名稱
    movies_title = []
    # 上映日期
    date = []
    # 預告片
    movies_pre = []
    # 評價
    movies_star = []
    # 電影圖片
    img_link = []
    # 電影簡介
    movies_text = []
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
            # 找圖片 電影簡介
            movie_url = link[index - 1]
            movie_rs = requests.session()
            movie_res = movie_rs.get(movie_url, verify=False)
            movie_res.encoding = 'utf-8'
            movie_soup = BeautifulSoup(movie_res.text, 'html.parser')
            movies_info_text = movie_soup.select_one('#story')
            movies_text.append(movies_info_text.text.lstrip())
            movie_img_data = movie_soup.select_one('div .movie_intro_foto img')
            img_link.append(movie_img_data['src'])
        else:
            link.append('')
            img_link.append('')
            movies_text.append('')
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
    for i in range(7):
        if (movies_dic['link'][i] != ''):
            detail = '上映日期 ： ' + movies_dic['date'][i] + '\n' + '網友滿意度 ： ' + str((float(movies_dic['movies_star'][i])) * 20) + '\n' + '劇情介紹 ： ' + movies_dic['movies_text'][i]
            carousel_data = CarouselColumn(
                thumbnail_image_url=movies_dic['img_link'][i],
                title=movies_dic['title'][i][0:40],
                text=detail[0:60],
                actions=[
                    URIAction(label='詳細內容', uri=movies_dic['link'][i]),
                    URIAction(label='預告片', uri=movies_dic['movies_pre'][i]),
                    PostbackAction(label='加入最愛', data='movie,'+movies_dic['link'][i])
                ]
            )
        else:
            carousel_data = CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/C33VNBj.png',
                title=movies_dic['title'][i][0:40],
                text='上映日期：'+movies_dic['date'][i],
                actions=[
                    URIAction(label='詳細內容',
                              uri='https://i.imgur.com/C33VNBj.png'),
                    URIAction(label='預告片',
                              uri='https://i.imgur.com/C33VNBj.png'),
                    PostbackAction(label='加入最愛', data='No')
                ]
            )
        carousel_group.append(carousel_data)
        # print(movies_dic['link'][i])
        # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
    carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
    push_template_message(event, template_message)
    return True

def show_hot_movies_pre(event):
    requests.packages.urllib3.disable_warnings()
    # 預告片榜
    target_url = 'https://movies.yahoo.com.tw/chart.html?cate=trailer'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    # 電影連結
    link = []
    # 電影名稱
    movies_title = []
    # 上映日期
    date = []
    # 預告片
    movies_pre = []
    # 評價
    movies_star = []
    # 電影圖片
    img_link = []
    # 電影簡介
    movies_text = []
    carousel_group = []
    # content = ""
    # 改 list 1,2,3
    for index, datas in enumerate(soup.select('div.rank_list.table.rankstyle3 div.tr')):
        if index == 0:
            continue
        # index-1 -> 找的數量
        if index == 8:
            break
        movie_info = datas.find_all('div')
        non = movie_info[1].find('a')
        if non != None:
            link.append(non['href'])
            # 找圖片 電影簡介
            movie_url = link[index - 1]
            movie_rs = requests.session()
            movie_res = movie_rs.get(movie_url, verify=False)
            movie_res.encoding = 'utf-8'
            movie_soup = BeautifulSoup(movie_res.text, 'html.parser')
            movies_info_text = movie_soup.select_one('#story')
            movies_text.append(movies_info_text.text.lstrip())
            movie_img_data = movie_soup.select_one('div .movie_intro_foto img')
            img_link.append(movie_img_data['src'])
        else:
            link.append('')
            movies_text.append('')
            img_link.append('')
        if index == 1:
            movies_title.append(movie_info[1].find('h2').text)
            date.append(movie_info[2].text)
            non = movie_info[3].find('a')
            # 找預告片
            if non != None:
                movies_pre.append(non['href'])
            else:
                movies_pre.append('')
            non = movie_info[4].find('h6')
            # 找評價星星
            if non != None:
                movies_star.append(non.text)
            else:
                movies_star.append('')
        else:
            movies_title.append(movie_info[1].find('div', 'rank_txt').text)
            date.append(movie_info[3].text)
            non = movie_info[4].find('a')
            # 找預告片
            if non != None:
                movies_pre.append(non['href'])
            else:
                movies_pre.append('')
            non = movie_info[5].find('h6')
            # 找評價星星
            if non != None:
                movies_star.append(non.text)
            else:
                movies_star.append('')
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
    for i in range(7):
        if (movies_dic['link'][i] != ''):
            detail = '上映日期 ： ' + movies_dic['date'][i] + '\n' + '網友滿意度 ： ' + str((float(movies_dic['movies_star'][i])) * 20) + '\n' + '劇情介紹 ： ' + movies_dic['movies_text'][i]
            carousel_data = CarouselColumn(
                thumbnail_image_url=movies_dic['img_link'][i],
                title=movies_dic['title'][i][0:40],
                text=detail[0:60],
                actions=[
                    URIAction(label='詳細內容', uri=movies_dic['link'][i]),
                    URIAction(label='預告片', uri=movies_dic['movies_pre'][i]),
                    PostbackAction(label='加入最愛', data='movie,'+ movies_dic['link'][i])
                ]
            )
        else:
            carousel_data = CarouselColumn(
                thumbnail_image_url='https://i.imgur.com/C33VNBj.png',
                title=movies_dic['title'][i][0:40],
                text='上映日期：'+movies_dic['date'][i],
                actions=[
                    URIAction(label='詳細內容',
                              uri='https://i.imgur.com/C33VNBj.png'),
                    URIAction(label='預告片',
                              uri='https://i.imgur.com/C33VNBj.png'),
                    PostbackAction(label='加入最愛', data='No')
                ]
            )
        carousel_group.append(carousel_data)
        # print(movies_dic['link'][i])
        # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
    carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
    push_template_message(event, template_message)
    return  True

def show_movies_news(event):
    requests.packages.urllib3.disable_warnings()
    # 新聞
    target_url = 'https://movies.yahoo.com.tw/tagged/movieheadline'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    # 連結
    link = []
    # 新聞標題
    news_title = []
    # 圖片連結
    img_link = []
    imagecarousel_group = []
    # content = ""
    for index, datas in enumerate(soup.select('li.news_content')):
        # index -> 找的數量
        if index == 10:
            break
        link.append(datas.find('a')['href'])
        img_link.append(datas.find('img')['src'])
        news_title.append(datas.find('h2').text)

    # 製作line 回復訊息
    x = ['title', 'img_link', 'link']
    movies_group = []
    movies_group.append(news_title)
    movies_group.append(img_link)
    movies_group.append(link)
    movies_dic = dict(zip(x, movies_group))
    for i in range(len(news_title)):
        imagecarouse_data = ImageCarouselColumn(
            image_url=movies_dic['img_link'][i],
            action=URIAction(
                uri=movies_dic['link'][i],
                label=movies_dic['title'][i][0:12])
        )
        imagecarousel_group.append(imagecarouse_data)

    image_carousel_template = ImageCarouselTemplate(columns=imagecarousel_group)
    template_message = TemplateSendMessage(alt_text='ImageCarousel alt text', template=image_carousel_template)
    push_template_message(event, template_message)
    return True

def search_moive(event, searchname):
    requests.packages.urllib3.disable_warnings()
    # 查電影
    target_url = 'https://movies.yahoo.com.tw/moviesearch_result.html?keyword=' + searchname + '&type=movie'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    # 電影連結
    link = []
    # 電影名稱
    movies_title = []
    # 上映日期
    date = []
    # 預告片
    movies_pre = []
    # 評價
    movies_star = []
    # 電影圖片
    img_link = []
    # 電影簡介
    # movies_text = []
    carousel_group = []
    # content = ""
    search = soup.select_one('div.searchpage')
    # 總共查到幾筆資料
    search_num_c = search.find('div', 'search_num _c').span.text
    if search_num_c != '0':
        for index, datas in enumerate(search.select('ul.release_list.mlist li')):
            # index -> 找的數量
            if index == 10:
                break
            img_link.append(datas.find('img')['src'])
            movie_info_u = datas.find('div', 'searchpage_info')
            movie_info_l = datas.find('div', 'release_btn')
            movie_info = movie_info_u.find('div', 'release_movie_name')
            link.append(movie_info.find('a')['href'])
            movies_title.append(movie_info.find('a').text.lstrip())
            movies_star.append('網友滿意度 ： ' + str((float(movie_info.find('dl', 'levelbox').dd.span.text)) * 20) if movie_info.find('dl', 'levelbox').dd.span != None else '網友期待度 ： ' + movie_info.find('dl', 'levelbox').dt.span.text)
            date.append(movie_info.find('div', 'time').text)
            # movies_text.append(movie_info_u.find('div', 'release_text').span.text.lstrip())
            # 找預告片 有處理找不到的意外
            movies_pre.append(movie_info_l.find('a', 'btn_s_vedio').get('href') if movie_info_l.find('a', 'btn_s_vedio').get('href') != None else '')

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
        for i in range(len(movies_title)):
            detail = movies_dic['date'][i] + '\n' + movies_dic['movies_star'][i]
            carousel_data = CarouselColumn(
                thumbnail_image_url=movies_dic['img_link'][i],
                title=movies_dic['title'][i][0:40],
                text=detail[0:60],
                actions=[
                    URIAction(label='詳細內容', uri=movies_dic['link'][i]),
                    URIAction(label='預告片', uri=movies_dic['movies_pre'][i] if movies_dic['movies_pre'][i] != '' else movies_dic['img_link'][i]),
                    PostbackAction(label='加入最愛', data='movie,'+movies_dic['link'][i])
                ]
            )
            carousel_group.append(carousel_data)
            # print(movies_dic['link'][i])
            # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
        carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
        template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
        push_template_message(event, template_message)
    else:
        mesg = '您的電影搜尋結果：共 ' + search_num_c + '筆，符合' + searchname
        push_text_message(event, mesg)
    return True

def animate_new_season(event, choice):
    requests.packages.urllib3.disable_warnings()
    num = '1' if choice == '週一' else '2' if choice == '週二' else '3' if choice == '週三' else '4' if choice == '週四' else '5' if choice == '週五' else '6' if choice == '週六' else '7'
    # 查動畫新番
    target_url = 'https://acg.gamer.com.tw/quarterly.php?d=' + num
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    # 動畫連結
    link = []
    # 動畫名稱
    animates_title = []
    # 上映日期
    date = []
    # 評分
    animates_star = []
    # 人氣
    animates_hot = []
    # 動畫圖片
    img_link = []
    # 動畫類別
    animates_text = []
    carousel_group = []
    # content = ""
    for index, datas in enumerate(soup.select('div.ACG-mainbox1')):
        # index -> 找的數量
        if index == 10:
            break
        acg_info = datas.find('div', 'ACG-mainbox2')
        link.append('https:' + acg_info.find('h1', 'ACG-maintitle').find('a')['href'])
        animates_title.append(acg_info.find('h1', 'ACG-maintitle').find('a').text)
        type = acg_info.find_all('ul')
        # more_type[1] 放心得 , more_type[2] 放相關新聞
        more_type = type[0].find_all('li')
        date.append(more_type[0].text)
        animates_text.append(type[1].li.text)
        img_link.append(acg_info.find('div', 'ACG-mainbox2B').a.img['src'])
        animates_star.append('評分：' + datas.find('div', 'ACG-mainbox4').find('p', 'ACG-mainboxpoint').span.text)
        animates_hot.append('人氣：' + datas.find('div', 'ACG-mainbox4').find('p', 'ACG-mainplay').span.text)

    page_now = soup.select_one('p.BH-pagebtnA').find('a', 'pagenow').text
    page = soup.select_one('p.BH-pagebtnA').find_all('a')
    page_num = len(page)
    # 製作line 回復訊息
    x = ['title', 'img_link', 'link', 'date', 'animates_star', 'animates_text', 'animates_hot']
    animates_group = []
    animates_group.append(animates_title)
    animates_group.append(img_link)
    animates_group.append(link)
    animates_group.append(date)
    animates_group.append(animates_star)
    animates_group.append(animates_text)
    animates_group.append(animates_hot)
    animates_dic = dict(zip(x, animates_group))
    for i in range(len(animates_title)):
        detail = animates_dic['date'][i] + '\n' + animates_dic['animates_hot'][i] + '　' + animates_dic['animates_star'][
            i] + '\n' + animates_dic['animates_text'][i]
        carousel_data = CarouselColumn(
            thumbnail_image_url=animates_dic['img_link'][i],
            title=animates_dic['title'][i][0:40],
            text=detail[0:60],
            actions=[
                URIAction(label='詳細內容', uri=animates_dic['link'][i]),
                # URIAction(label='相關新聞', uri=movies_dic['movies_pre'][i]),
                PostbackAction(label='加入最愛', data='animatehot,'+animates_dic['link'][i])
            ]
        )
        carousel_group.append(carousel_data)
        # print(movies_dic['link'][i])
        # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
    carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
    template_message1 = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)

    # 製作 下一頁訊息
    # if page_num == 1:
    # buttons_template = ButtonsTemplate(
    #         text='目前頁數 '+page_now+'/'+str(page_num),
    #         actions=[
    #             PostbackAction(label='返回', data='返回本季新作')
    #         ])
    # else:
    #     buttons_template = ButtonsTemplate(text='目前頁數 ' + page_now + '/' + str(page_num), actions=[
    #         PostbackAction(label='返回', data='返回本季新作'),
    #         PostbackAction(label='下一頁', data='下一頁,'+'https://acg.gamer.com.tw/'+page[int(page_now)]['href'])
    #     ])
    # template_message2 = TemplateSendMessage(alt_text = 'Buttons alt text', template = buttons_template)
    push_template_message(event, template_message1)
    # push_text_message(event, '目前頁數 '+page_now+'/'+str(page_num))
    return True

def show_animate_leaderboard(event):
    buttons_template = ButtonsTemplate(
        title = '排行榜',
        text = '請按下方選項',
        actions = [
            PostbackAction(label = '人氣排行榜', data = '人氣'),
            PostbackAction(label = '評分排行榜', data = '評分'),
            PostbackAction(label = '期待排行榜', data = '期待')
        ])
    template_message = TemplateSendMessage(alt_text = 'Buttons alt text', template = buttons_template)
    push_template_message(event, template_message)
    return True

def show_hot_animate(event, chart):
    requests.packages.urllib3.disable_warnings()
    # 查 排行
    if chart == '人氣':
        target_url = 'https://acg.gamer.com.tw/billboard.php?t=2&p=anime'
    elif chart == '評分':
        target_url = 'https://acg.gamer.com.tw/billboard.php?t=3&p=anime'
    elif chart == '期待':
        target_url = 'https://acg.gamer.com.tw/billboard.php?t=4&p=anime'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    # 動畫連結
    link = []
    # 動畫名稱
    animates_title = []
    # 上映日期
    date = []
    # 評分
    animates_star = []
    # 人氣
    animates_hot = []
    # 動畫圖片
    img_link = []
    # 動畫類別
    animates_text = []
    carousel_group = []
    # content = ""
    for index, datas in enumerate(soup.select('div.ACG-mainbox1')):
        # index-1 -> 找的數量
        if index == 10:
            break
        acg_info = datas.find('div', 'ACG-mainbox2')
        link.append('https:' + acg_info.find('h1', 'ACG-maintitle').find('a')['href'])
        animates_title.append(acg_info.find('h1', 'ACG-maintitle').find('a').text)
        type = acg_info.find_all('ul')
        # more_type[1] 放心得 , more_type[2] 放相關新聞
        more_type = type[0].find_all('li')
        date.append(more_type[0].text)
        animates_text.append(type[1].li.text)
        img_link.append(acg_info.find('div', 'ACG-mainbox2B').a.img['src'])
        animates_star.append('評分：' + datas.find('div', 'ACG-mainbox4').find('p', 'ACG-mainboxpoint').span.text)
        animates_hot.append('人氣：' + datas.find('div', 'ACG-mainbox4').find('p', 'ACG-mainplay').span.text)

    # 製作line 回復訊息
    x = ['title', 'img_link', 'link', 'date', 'animates_star', 'animates_text', 'animates_hot']
    animates_group = []
    animates_group.append(animates_title)
    animates_group.append(img_link)
    animates_group.append(link)
    animates_group.append(date)
    animates_group.append(animates_star)
    animates_group.append(animates_text)
    animates_group.append(animates_hot)
    animates_dic = dict(zip(x, animates_group))
    for i in range(len(animates_title)):
        detail = animates_dic['date'][i] + '\n' + animates_dic['animates_hot'][i] + '　' + animates_dic['animates_star'][i] + '\n' + animates_dic['animates_text'][i]
        carousel_data = CarouselColumn(
            thumbnail_image_url=animates_dic['img_link'][i],
            title=animates_dic['title'][i][0:40],
            text=detail[0:60],
            actions=[
                URIAction(label='詳細內容', uri=animates_dic['link'][i]),
                # URIAction(label='相關新聞', uri=movies_dic['movies_pre'][i]),
                PostbackAction(label='加入最愛', data='animate,'+animates_dic['link'][i])
            ]
        )
        carousel_group.append(carousel_data)
        # print(movies_dic['link'][i])
        # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
    carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
    push_template_message(event, template_message)
    return True

def show_animates_news(event):
    requests.packages.urllib3.disable_warnings()
    # 查 新聞
    target_url = 'https://acg.gamer.com.tw/news.php?p=anime'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    # 新聞連結
    link = []
    # 新聞名稱
    news_title = []
    # 新聞圖片
    img_link = []
    imagecarousel_group = []
    # content = ""
    for index, datas in enumerate(soup.select('div.BH-lbox.GN-lbox2 div.GN-lbox2B')):
        # index -> 找的數量
        if index == 10:
            break
        link.append('https:' + datas.find('div', 'GN-lbox2E').find('a')['href'])
        img_link.append(datas.find('div', 'GN-lbox2E').find('img')['src'])
        news_title.append(datas.find('h1', 'GN-lbox2D').find('a').text)

    # 製作line 回復訊息
    x = ['title', 'img_link', 'link']
    movies_group = []
    movies_group.append(news_title)
    movies_group.append(img_link)
    movies_group.append(link)
    movies_dic = dict(zip(x, movies_group))
    for i in range(len(news_title)):
        imagecarouse_data = ImageCarouselColumn(
            image_url=movies_dic['img_link'][i],
            action=URIAction(
                uri=movies_dic['link'][i],
                label=movies_dic['title'][i][0:12])
        )
        imagecarousel_group.append(imagecarouse_data)

    image_carousel_template = ImageCarouselTemplate(columns=imagecarousel_group)
    template_message = TemplateSendMessage(alt_text='ImageCarousel alt text', template=image_carousel_template)
    push_template_message(event, template_message)
    return True

def search_animate(event, searchname):
    requests.packages.urllib3.disable_warnings()
    # 查 新聞
    target_url = 'https://acg.gamer.com.tw/search.php?sp=t4&kw=' + searchname
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    # 動畫連結
    link = []
    # 動畫名稱
    animates_title = []
    # 動畫圖片
    img_link = []
    # 動畫簡介
    animates_text = []
    carousel_group = []
    # content = ""
    # 找到幾筆
    if soup.select_one('div.BH-lbox.GU-lbox9').find('p', {'align':'center'}) != None:
        search_num = soup.select_one('div.BH-lbox.GU-lbox9').find('p', {'align':'center'}).span.text
        for index, datas in enumerate(soup.select('div.BH-lbox.GU-lbox9 table.search_table')):
            # index -> 找的數量
            if index == 10:
                break
            animates_text.append(datas.find('td', {'valign':'top'}).text.lstrip().splitlines()[2][:-4])
            animates_title.append(datas.find('td', {'valign':'top'}).text.lstrip().splitlines()[1])
            link.append('https:' + datas.find('td', {'valign':'top'}).find('p', 'search_title').a['href'])
            img_link.append(datas.find('td', {'align':'center'}).img['src'])

        # 製作line 回復訊息
        x = ['title', 'img_link', 'link', 'animates_text']
        animates_group = []
        animates_group.append(animates_title)
        animates_group.append(img_link)
        animates_group.append(link)
        animates_group.append(animates_text)
        animates_dic = dict(zip(x, animates_group))
        for i in range(len(animates_title)):
            carousel_data = CarouselColumn(
                thumbnail_image_url=animates_dic['img_link'][i],
                title=animates_dic['title'][i][0:40],
                text=animates_dic['animates_text'][i][0:60],
                actions=[
                    URIAction(label='詳細內容', uri=animates_dic['link'][i]),
                    # URIAction(label='相關新聞', uri=movies_dic['movies_pre'][i]),
                    PostbackAction(label='加入最愛', data='animate,'+animates_dic['link'][i])
                ]
            )
            carousel_group.append(carousel_data)
            # print(movies_dic['link'][i])
            # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
        carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
        template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
        push_template_message(event, template_message)
    else:
        mesg = '您的動畫搜尋結果：共 0 筆，符合' + searchname
        push_text_message(event, mesg)
    return True

def add_favorite(event, data):
    url = data.split(',')
    if url[0] == 'movie':
        if url[1] in favorite_movies[event.source.user_id]:
            push_text_message(event, '已在我的最愛')
            return True
        else:
            if len(favorite_movies[event.source.user_id]) < 10:
                favorite_movies[event.source.user_id].append(url[1])
                push_text_message(event, '成功加入我的最愛')
            else:
                push_text_message(event, '我的最愛已滿(最多10個)')
                return True
    else:
        if url[1] in favorite_animates[event.source.user_id]:
            push_text_message(event, '已在我的最愛')
            return True
        else:
            if len(favorite_animates[event.source.user_id]) < 10:
                favorite_animates[event.source.user_id].append(url[1])
                push_text_message(event, '成功加入我的最愛')
            else:
                push_text_message(event, '我的最愛已滿(最多10個)')
                return True
    return True

def my_favorite_confirm(event):
    confirm_template = ConfirmTemplate(text='我的動畫 or 我的電影?', actions=[
        PostbackAction(label='我的動畫', data='動畫'),
        PostbackAction(label='我的電影', data='電影')
    ])
    template_message = TemplateSendMessage(alt_text='Confirm alt text', template=confirm_template)
    push_template_message(event, template_message)
    return True

def show_favorite(event, text):
    if text == "動畫" or text == "animate":
        if len(favorite_animates[event.source.user_id]) != 0:
            carousel_group = []
            for target_url in favorite_animates[event.source.user_id]:
                requests.packages.urllib3.disable_warnings()
                # 印 我的最愛
                rs = requests.session()
                res = rs.get(target_url, verify=False)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                # content = ""
                datas = soup.select_one('div.BH-lbox.ACG-mster_box1.hreview-aggregate.hreview')
                title = datas.find('h1').text
                detail = datas.find('ul', 'ACG-box1listA').text.strip()
                img_link = datas.find('div', 'ACG-box1-left').img['src']

                # 製作line 回復訊息
                carousel_data = CarouselColumn(
                        thumbnail_image_url=img_link,
                        title=title[0:40],
                        text=detail[0:60],
                        actions=[
                        URIAction(label='詳細內容', uri=target_url),
                        # URIAction(label='相關新聞', uri=movies_dic['movies_pre'][i]),
                        PostbackAction(label='移除最愛', data='delete,animate,' + target_url)
                    ]
                )
                carousel_group.append(carousel_data)
                # print(movies_dic['link'][i])
                # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
            carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
            template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
            push_template_message(event, template_message)
        else:
            push_text_message(event, '我的最愛目前沒有內容，請返回我的最愛~')
    else:
        if len(favorite_movies[event.source.user_id]) != 0:
            carousel_group = []
            for target_url in favorite_movies[event.source.user_id]:
                requests.packages.urllib3.disable_warnings()
                # 印 我的最愛
                rs = requests.session()
                res = rs.get(target_url, verify=False)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                # content = ""
                datas = soup.select_one('div #content_l')
                title = datas.find('div', 'movie_intro_info_r').h1.text
                date = datas.find('div', 'movie_intro_info_r').span.text
                img_link = datas.find('div', 'movie_intro_info_l').img['src']
                movie_pre = datas.find('div', 'l_box have_arbox _c').a['href']

                # 製作line 回復訊息
                carousel_data = CarouselColumn(
                    thumbnail_image_url=img_link,
                    title=title[0:40],
                    text=date[0:60],
                    actions=[
                        URIAction(label='詳細內容', uri=target_url),
                        URIAction(label='預告片', uri=movie_pre),
                        PostbackAction(label='移除最愛', data='delete,movie,' + target_url)
                    ]
                )
                carousel_group.append(carousel_data)
                # print(movies_dic['link'][i])
                # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
            carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
            template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
            push_template_message(event, template_message)
        else:
            push_text_message(event, '我的最愛目前沒有內容，請返回我的最愛~')
    return True

def delete_favorite(event, data):
    url = data.split(',')
    if url[0] == 'movie':
        if url[1] in favorite_movies[event.source.user_id]:
            favorite_movies[event.source.user_id].remove(url[1])
            return True
    else:
        if url[1] in favorite_animates[event.source.user_id]:
            favorite_animates[event.source.user_id].remove(url[1])
            return True
    return True

def do_game(event, text):
    if text == '石頭':
        catch = random.randint(1, 3)
        if (catch == 2):
            push_text_message(event, '剪刀')
            win_game[event.source.user_id] += 1
        elif (catch == 3):
            push_text_message(event, '布')
            if win_game[event.source.user_id] > 0:
                win_game[event.source.user_id] -= 1
        else:
            push_text_message(event, '石頭')
    elif text == '剪刀':
        catch = random.randint(1, 3)
        if (catch == 3):
            push_text_message(event, '布')
            win_game[event.source.user_id] += 1
        elif (catch == 1):
            push_text_message(event, '石頭')
            if win_game[event.source.user_id] > 0:
                win_game[event.source.user_id] -= 1
        else:
            push_text_message(event, '剪刀')
    elif text == '布':
        catch = random.randint(1, 3)
        if (catch == 1):
            push_text_message(event, '石頭')
            win_game[event.source.user_id] += 1
        elif (catch == 2):
            push_text_message(event, '剪刀')
            if win_game[event.source.user_id] > 0:
                win_game[event.source.user_id] -= 1
        else:
            push_text_message(event, '布')
    push_text_message(event, '目前連贏 '+str(win_game[event.source.user_id]) +' 次')
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
