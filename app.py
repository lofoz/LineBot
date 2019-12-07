import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, PostbackEvent

from fsm import TocMachine

from machine_data import  machineData

load_dotenv()

machine = {}

# machine = TocMachine(
#     states=[
#         "main_menu",
#         "movie_lobby",
#         "animation_lobby",
#         "game_lobby",
#         "new_movie",
#         "hot_movie",
#         "movie_leaderboard",
#         "movie_news",
#         "search_movie",
#         "do_search_movie",
#         "animate_new_season",
#         "do_animate_new_season"
#     ],
#     transitions=[
#         {
#             "trigger": "advance",
#             "source": "main_menu",
#             "dest": "movie_lobby",
#             "conditions": "is_going_to_movie_lobby",
#         },
#         {
#             "trigger": "advance",
#             "source": "main_menu",
#             "dest": "animation_lobby",
#             "conditions": "is_going_to_animation_lobby",
#         },
#         {
#             "trigger": "advance",
#             "source": "main_menu",
#             "dest": "game_lobby",
#             "conditions": "is_going_to_game_lobby",
#         },
#         {
#             "trigger": "advance",
#             "source": "movie_lobby",
#             "dest": "new_movie",
#             "conditions": "is_going_to_new_movie",
#         },
#         {
#             "trigger": "advance",
#             "source": "movie_lobby",
#             "dest": "movie_leaderboard",
#             "conditions": "is_going_to_movie_leaderboard",
#         },
#         {
#             "trigger": "advance",
#             "source": "movie_lobby",
#             "dest": "movie_news",
#             "conditions": "is_going_to_movie_news",
#         },
#         {
#             "trigger": "advance_postback",
#             "source": "movie_lobby",
#             "dest": "hot_movie",
#             "conditions": "is_going_to_hot_movie",
#         },
#         {
#             "trigger": "advance",
#             "source": "movie_lobby",
#             "dest": "search_movie",
#             "conditions": "is_going_to_search_movie",
#         },
#         {
#             "trigger": "advance",
#             "source": "search_movie",
#             "dest": "do_search_movie",
#         },
#         {
#             "trigger": "advance",
#             "source": "animation_lobby",
#             "dest": "animate_new_season",
#             "conditions": "is_going_to_animate_new_season",
#         },
#         {
#             "trigger": "advance",
#             "source": "animate_new_season",
#             "dest": "do_animate_new_season",
#             "conditions": "is_going_to_do_animate_new_season",
#         },
#         # 按下返回主選單
#         {
#             "trigger": "advance",
#             "source": ["movie_lobby", "animation_lobby", "game_lobby"],
#             "dest": "main_menu",
#             "conditions": "is_going_to_main_menu",
#         },
#         # 無條件返回 movie_lobby
#         {
#             "trigger": "go_back_movie_lobby",
#             "source": ["new_movie", "hot_movie", "movie_leaderboard", "movie_news", "do_search_movie"],
#             "dest": "movie_lobby",
#         },
#         # 按下返回動畫選單
#         {
#             "trigger": "advance",
#             "source": "animate_new_season",
#             "dest": "animation_lobby",
#             "conditions": "is_going_to_animation_lobby",
#         },
#         # 無條件返回 animate_new_season
#         {
#             "trigger": "go_back_animate_new_season",
#             "source": "do_animate_new_season",
#             "dest": "animate_new_season",
#         },
#     ],
#     initial="main_menu",
#     auto_transitions=False,
#     show_conditions=True,
# )

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
        if event.source.user_id not in machine:
            machine[event.source.user_id] = TocMachine(
                states=machineData["states"],
                transitions=machineData["transitions"],
                initial=machineData["initial"],
                auto_transitions=machineData["auto_transitions"],
                show_conditions=machineData["show_conditions"]
            )
        if isinstance(event, MessageEvent):
            if isinstance(event.message, TextMessage) and isinstance(event.message.text, str):
                response = machine[event.source.user_id].advance(event)
        elif isinstance(event, PostbackEvent):
            if isinstance(event.postback.data, str):
                response = machine[event.source.user_id].advance_postback(event)
        print(f"\nFSM STATE: {machine[event.source.user_id].state}")
        print(f"REQUEST BODY: \n{body}")
        #if response == False:
            #send_text_message(event.reply_token, "Not Entering any State")

    return "OK"
	


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    if "graph" not in machine:
        machine["graph"] = TocMachine(
            states=machineData["states"],
            transitions=machineData["transitions"],
            initial=machineData["initial"],
            auto_transitions=machineData["auto_transitions"],
            show_conditions=machineData["show_conditions"]
        )
    machine["graph"].get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT")
    app.run(host="0.0.0.0", port=port, debug=True)
