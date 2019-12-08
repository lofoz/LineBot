from transitions.extensions import GraphMachine

from utils import (
    send_text_message, SwitchMenuTo, show_new_movies, show_hot_movies,
    show_movie_leaderboard, show_hot_movies_pre, show_movies_news,
    search_moive, animate_new_season, show_animate_leaderboard,
    show_hot_animate,
    show_animates_news,
    search_animate,
    add_favorite,
    favorite_movies,
    favorite_animates,
    my_favorite_confirm,
    show_favorite,
    delete_favorite
)

machine = {}
favorite_state = {}

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_main_menu(self, event):
        text = event.message.text
        return text.lower() == "返回主選單"

    def on_enter_main_menu(self, event):
        SwitchMenuTo("mainmenu", event)
        print("I'm entering main_menu")

    def is_going_to_movie_lobby(self, event):
        text = event.message.text
        return text.lower() == "電影選單"

    def is_going_to_movie_lobby_postback(self, event):
        text = event.postback.data
        return text.lower() == "返回電影選單"

    def on_enter_movie_lobby(self, event):
        SwitchMenuTo("moviemenu", event)
        print("I'm entering movie_lobby")

    #def on_exit_movie_lobby(self):
    #    print("Leaving movie_lobby")

    def is_going_to_animation_lobby(self, event):
        text = event.message.text
        return text.lower() == "動畫選單" or text.lower() == "返回動畫選單"

    def is_going_to_animation_lobby_postback(self, event):
        text = event.postback.data
        return text.lower() == "返回動畫選單"

    def on_enter_animation_lobby(self, event):
        SwitchMenuTo("animatemenu", event)
        print("I'm entering animation_lobby")

    def is_going_to_game_lobby(self, event):
        text = event.message.text
        return text.lower() == "遊戲選單"

    def on_enter_game_lobby(self, event):
        SwitchMenuTo("Submenu", event)
        print("I'm entering game_lobby")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger game_lobby")

    def is_going_to_new_movie(self, event):
        text = event.message.text
        return text.lower() == "最新電影"

    def on_enter_new_movie(self, event):
        print("I'm entering new_movie")
        reply_token = event.reply_token
        show_new_movies(reply_token)
        self.go_back_movie_lobby(event)

    def is_going_to_movie_leaderboard(self, event):
        text = event.message.text
        return text.lower() == "排行榜"

    def on_enter_movie_leaderboard(self, event):
        print("I'm entering movie_leaderboard")
        reply_token = event.reply_token
        show_movie_leaderboard(reply_token)
        self.go_back_movie_lobby(event)

    def is_going_to_hot_movie(self, event):
        text = event.postback.data
        return text.lower() == "台北票房榜" or text.lower() == "全美票房榜" or text.lower() == "年度票房榜" or text.lower() == "預告片榜"

    def on_enter_hot_movie(self, event):
        print("I'm entering hot_movie")
        text = event.postback.data
        reply_token = event.reply_token
        if text.lower() == "預告片榜":
            show_hot_movies_pre(reply_token)
        else:
            show_hot_movies(reply_token, text.lower())
        self.go_back_movie_lobby(event)

    def is_going_to_movie_news(self, event):
        text = event.message.text
        return text.lower() == "電影新聞"

    def on_enter_movie_news(self, event):
        print("I'm entering movie_news")
        reply_token = event.reply_token
        show_movies_news(reply_token)
        self.go_back_movie_lobby(event)

    def is_going_to_search_movie(self, event):
        text = event.message.text
        return text.lower() == "查電影"

    def on_enter_search_movie(self, event):
        SwitchMenuTo("searchmovie", event)
        print("I'm entering search_movie")
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入欲查詢電影")

    def on_enter_do_search_movie(self, event):
        print("I'm entering do_search_movie")
        reply_token = event.reply_token
        search_moive(reply_token, event.message.text)
        self.go_back_movie_lobby(event)

    def on_enter_animate_new_season(self, event):
        SwitchMenuTo("seasonanimate", event)
        print("I'm entering animate_new_season")

    def is_going_to_animate_new_season(self, event):
        text = event.message.text
        return text.lower() == "本季新作"

    def on_enter_do_animate_new_season(self, event):
        print("I'm entering animate_new_season")
        reply_token = event.reply_token
        animate_new_season(reply_token, event.postback.data)
        self.go_back_animate_new_season(event)

    def is_going_to_do_animate_new_season(self, event):
        text = event.postback.data
        return text.lower() == "週一" or text.lower() == "週二" or text.lower() == "週三" or text.lower() == "週四" or text.lower() == "週五" or text.lower() == "週六" or text.lower() == "週日"

    def is_going_to_animate_leaderboard(self, event):
        text = event.message.text
        return text.lower() == "排行榜"

    def on_enter_animate_leaderboard(self, event):
        print("I'm entering animate_leaderboard")
        reply_token = event.reply_token
        show_animate_leaderboard(reply_token)
        self.go_back_animation_lobby(event)

    def is_going_to_hot_animate(self, event):
        text = event.postback.data
        return text.lower() == "人氣" or text.lower() == "評分" or text.lower() == "期待"

    def on_enter_hot_animate(self, event):
        print("I'm entering hot_animate")
        text = event.postback.data
        reply_token = event.reply_token
        show_hot_animate(reply_token, text.lower())
        self.go_back_animation_lobby(event)

    def is_going_to_animate_news(self, event):
        text = event.message.text
        return text.lower() == "動畫新聞"

    def on_enter_animate_news(self, event):
        print("I'm entering animate_news")
        reply_token = event.reply_token
        show_animates_news(reply_token)
        self.go_back_animation_lobby(event)

    def is_going_to_search_animate(self, event):
        text = event.message.text
        return text.lower() == "查動畫"

    def on_enter_search_animate(self, event):
        SwitchMenuTo("searchanimate", event)
        print("I'm entering search_animate")
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入欲查詢動畫")

    def on_enter_do_search_animate(self, event):
        print("I'm entering do_search_animate")
        reply_token = event.reply_token
        search_animate(reply_token, event.message.text)
        self.go_back_animation_lobby(event)

    def is_going_to_add_favorite(self, event):
        text = event.postback.data
        data = text.split(',')[0]
        return data == 'movie' or data == 'animate' or data == 'animatehot'

    def on_enter_add_favorite(self, event):
        print("I'm entering add_favorite")
        text = event.postback.data
        data = text.split(',')[0]
        add_favorite(event, text)
        if data == 'movie':
            self.go_back_movie_lobby(event)
        elif data == 'animate':
            self.go_back_animation_lobby(event)
        else:
            self.go_back_animate_new_season(event)

    def is_going_to_my_favorite(self, event):
        text = event.message.text
        favorite_state[event.source.user_id] = machine[event.source.user_id].state
        return text == '我的最愛'

    def is_going_to_my_favorite_postback(self, event):
        text = event.postback.data
        favorite_state[event.source.user_id] = machine[event.source.user_id].state
        return text == '我的最愛'

    def is_going_to_show_favorite_my(self, event):
        text = event.message.text
        return text == '返回我的最愛'

    def on_enter_my_favorite(self, event):
        SwitchMenuTo("myfavorite", event)
        print("I'm entering my_favorite")
        reply_token = event.reply_token
        my_favorite_confirm(reply_token)

    def is_going_to_show_favorite(self, event):
        text = event.postback.data
        return text == '動畫' or text == '電影'

    def on_enter_show_favorite(self, event):
        SwitchMenuTo("backmyfavorite", event)
        print("I'm entering show_favorite")
        text = event.postback.data
        show_favorite(event, text)

    def is_going_to_leave_favorite(self, event):
        text = event.message.text
        return text == '返回'

    def on_enter_leave_favorite(self, event):
        print("I'm entering leave_favorite")
        if favorite_state[event.source.user_id] == "main_menu":
            self.go_back_main_menu(event)
        elif favorite_state[event.source.user_id] == "movie_lobby":
            self.go_back_movie_lobby(event)
        elif favorite_state[event.source.user_id] == "animation_lobby":
            self.go_back_animation_lobby(event)
        elif favorite_state[event.source.user_id] == "search_movie":
            self.go_back_search_movie(event)
        elif favorite_state[event.source.user_id] == "animate_new_season":
            self.go_back_animate_new_season(event)
        elif favorite_state[event.source.user_id] == "search_animate":
            self.go_back_search_animate(event)

    def is_going_to_delete_favorite(self, event):
        text = event.postback.data
        data = text.split(',')[0]
        return data == 'delete'

    def on_enter_delete_favorite(self, event):
        print("I'm entering add_favorite")
        text = event.postback.data
        data = text.split(',')
        text = data[1]+','+data[2]
        event.postback.data = data[1]
        delete_favorite(event, text)
        self.go_back_show_favorite(event)
