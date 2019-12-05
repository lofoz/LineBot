from transitions.extensions import GraphMachine

from utils import send_text_message, SwitchMenuTo, show_new_movies, show_hot_movies, show_movie_leaderboard

from linebot.models import MessageEvent, TextMessage, PostbackEvent


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
        return text.lower() == "動畫"

    def on_enter_animation_lobby(self, event):
        SwitchMenuTo("Submenu", event)
        print("I'm entering animation_lobby")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger animation_lobby")

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
        return text.lower() == "台北票房榜" or text.lower() == "全美票房榜" or text.lower() == "年度票房榜"

    def on_enter_hot_movie(self, event):
        print("I'm entering new_movie")
        text = event.postback.data
        reply_token = event.reply_token
        show_hot_movies(reply_token, text.lower())
        self.go_back_movie_lobby(event)
