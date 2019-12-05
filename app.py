import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, PostbackEvent

from fsm import TocMachine
from utils import send_text_message, SwitchMenuTo, show_new_movies, show_hot_movies_tw, show_hot_movies_us, show_hot_movies_un, show_movie_leaderboard

load_dotenv()


machine = TocMachine(
    states=[
        "main_menu",
        "movie_lobby",
        "animation_lobby",
        "game_lobby",
        "new_movie",
        "hot_movie",
        "movie_leaderboard"
    ],
    transitions=[
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "movie_lobby",
            "conditions": "is_going_to_movie_lobby",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "animation_lobby",
            "conditions": "is_going_to_animation_lobby",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "game_lobby",
            "conditions": "is_going_to_game_lobby",
        },
        {
            "trigger": "advance",
            "source": "movie_lobby",
            "dest": "new_movie",
            "conditions": "is_going_to_new_movie",
        },
        {
            "trigger": "advance",
            "source": "movie_lobby",
            "dest": "movie_leaderboard",
            "conditions": "is_going_to_movie_leaderboard",
        },
        {
            "trigger": "advance_postback",
            "source": "movie_lobby",
            "dest": "hot_movie",
            "conditions": "is_going_to_hot_movie",
        },
        # 按下返回主選單
        {
            "trigger": "advance",
            "source": ["movie_lobby", "animation_lobby", "game_lobby"],
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        # 無條件返回 movie_lobby
        {
            "trigger": "go_back_movie_lobby",
            "source": ["new_movie", "hot_movie", "movie_leaderboard"],
            "dest": "movie_lobby",
        },
    ],
    initial="main_menu",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.environ.get("LINE_CHANNEL_SECRET")
channel_access_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)
		
    for event in events:
        if isinstance(event, MessageEvent):
            if isinstance(event.message, TextMessage) and isinstance(event.message.text, str):
                response = machine.advance(event)
        elif isinstance(event, PostbackEvent):
            if isinstance(event.postback.data, str):
                response = machine.advance_postback(event)
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"
	


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT")
    app.run(host="0.0.0.0", port=port, debug=True)
