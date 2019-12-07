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
            title=movies_dic['title'][i][0:40],
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
    carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
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
            PostbackAction(label = '年度票房榜', data = '年度票房榜'),
            PostbackAction(label='預告片榜', data='預告片榜')
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
                    MessageAction(label='加入最愛', text='米')
                ]
            )
        else:
            carousel_data = CarouselColumn(
                thumbnail_image_url='https://movies.tw.campaign.yahoo.net/i/o/production/movies/August2019/vpVOFf6g6g3WiSd1qFTN-2764x4096.jpeg',
                title=movies_dic['title'][i][0:40],
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
    carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
    send_template_message(reply_token, template_message)
    return True

def show_hot_movies_pre(reply_token):
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
                    MessageAction(label='加入最愛', text='米')
                ]
            )
        else:
            carousel_data = CarouselColumn(
                thumbnail_image_url='https://movies.tw.campaign.yahoo.net/i/o/production/movies/August2019/vpVOFf6g6g3WiSd1qFTN-2764x4096.jpeg',
                title=movies_dic['title'][i][0:40],
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
    carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
    template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
    send_template_message(reply_token, template_message)
    return  True

def show_movies_news(reply_token):
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
        # index-1 -> 找的數量
        if index == 11:
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
    for i in range(10):
        imagecarouse_data = ImageCarouselColumn(
            image_url=movies_dic['img_link'][i],
            action=URIAction(
                uri=movies_dic['link'][i],
                label=movies_dic['title'][i][0:12])
        )
        imagecarousel_group.append(imagecarouse_data)

    image_carousel_template = ImageCarouselTemplate(columns=imagecarousel_group)
    template_message = TemplateSendMessage(alt_text='ImageCarousel alt text', template=image_carousel_template)
    send_template_message(reply_token, template_message)
    return True

def search_moive(reply_token, searchname):
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
            # index-1 -> 找的數量
            if index == 11:
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
                    MessageAction(label='加入最愛', text='米')
                ]
            )
            carousel_group.append(carousel_data)
            # print(movies_dic['link'][i])
            # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
        carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
        template_message = TemplateSendMessage(alt_text='Carousel alt text', template=carousel_template)
        send_template_message(reply_token, template_message)
    else:
        mesg = '您的電影搜尋結果：共 ' + search_num_c + '筆，符合' + searchname
        send_text_message(reply_token, mesg)
    return True

def animate_new_season(reply_token, choice):
    requests.packages.urllib3.disable_warnings()
    # 查動畫新番
    target_url = 'https://acg.gamer.com.tw/quarterly.php?d=' + choice
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
        if index == 11:
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
        detail = animates_dic['date'][i] + '\n' + animates_dic['animates_hot'][i] + '　' + animates_dic['animates_star'][
            i] + '\n' + animates_dic['animates_text'][i]
        carousel_data = CarouselColumn(
            thumbnail_image_url=animates_dic['img_link'][i],
            title=animates_dic['title'][i][0:40],
            text=detail[0:60],
            actions=[
                URIAction(label='詳細內容', uri=animates_dic['link'][i]),
                # URIAction(label='相關新聞', uri=movies_dic['movies_pre'][i]),
                MessageAction(label='加入最愛', text='米')
            ]
        )
        carousel_group.append(carousel_data)
        # print(movies_dic['link'][i])
        # content += '{}\n{}\n'.format(movies_dic['title'][i], movies_dic['link'][i])
    carousel_template = CarouselTemplate(columns=carousel_group, image_aspect_ratio='square', image_size='cover')
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
