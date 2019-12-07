from transitions.extensions import GraphMachine

from utils import send_text_message, SwitchMenuTo, show_new_movies, show_hot_movies, show_movie_leaderboard, show_hot_movies_pre, show_movies_news, search_moive, animate_new_season


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_main_menu(self, event):
        text = event.message.text
        return text.lower() == "返回主選單"

    def on_enter_main_menu(self, event):
        SwitchMenuTo("Mainmenu", event)
        print("I'm entering main_menu")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger main_menu")

    def is_going_to_movie_lobby(self, event):
        text = event.message.text
        return text.lower() == "電影"

    def on_enter_movie_lobby(self, event):
        SwitchMenuTo("Submenu", event)
        print("I'm entering movie_lobby")

    #def on_exit_movie_lobby(self):
    #    print("Leaving movie_lobby")

    def is_going_to_animation_lobby(self, event):
        text = event.message.text
        return text.lower() == "動畫" or text.lower() == "返回動畫選單"

    def on_enter_animation_lobby(self, event):
        SwitchMenuTo("Submenu", event)
        print("I'm entering animation_lobby")

    def is_going_to_game_lobby(self, event):
        text = event.message.text
        return text.lower() == "小遊戲"

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
        print("I'm entering new_movie")
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
        SwitchMenuTo("Submenu", event)
        print("I'm entering search_movie")
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入欲查詢電影")

    def on_enter_do_search_movie(self, event):
        print("I'm entering do_search_movie")
        reply_token = event.reply_token
        search_moive(reply_token, event.message.text)
        self.go_back_movie_lobby(event)

    def on_enter_animate_new_season(self, event):
        SwitchMenuTo("Submenu", event)
        print("I'm entering animate_new_season")

    def is_going_to_animate_new_season(self, event):
        text = event.message.text
        return text.lower() == "本季新作"

    def on_enter_do_animate_new_season(self, event):
        SwitchMenuTo("Submenu", event)
        print("I'm entering animate_new_season")
        reply_token = event.reply_token
        animate_new_season(reply_token, event.message.text)
        self.go_back_animate_new_season(event)

    def is_going_to_do_animate_new_season(self, event):
        text = event.message.text
        return text.lower() == "1" or text.lower() == "2" or text.lower() == "1" or text.lower() == "3" or text.lower() == "4" or text.lower() == "5" or text.lower() == "6" or text.lower() == "7"
