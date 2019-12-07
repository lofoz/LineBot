machineData = {
    "states" : [
        "main_menu",
        "movie_lobby",
        "animation_lobby",
        "game_lobby",
        "new_movie",
        "hot_movie",
        "movie_leaderboard",
        "movie_news",
        "search_movie",
        "do_search_movie",
        "animate_new_season",
        "do_animate_new_season"
    ],
    "transitions" : [
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
            "trigger": "advance",
            "source": "movie_lobby",
            "dest": "movie_news",
            "conditions": "is_going_to_movie_news",
        },
        {
            "trigger": "advance_postback",
            "source": "movie_lobby",
            "dest": "hot_movie",
            "conditions": "is_going_to_hot_movie",
        },
        {
            "trigger": "advance",
            "source": "movie_lobby",
            "dest": "search_movie",
            "conditions": "is_going_to_search_movie",
        },
        {
            "trigger": "advance",
            "source": "search_movie",
            "dest": "do_search_movie",
        },
        {
            "trigger": "advance",
            "source": "animation_lobby",
            "dest": "animate_new_season",
            "conditions": "is_going_to_animate_new_season",
        },
        {
            "trigger": "advance",
            "source": "animate_new_season",
            "dest": "do_animate_new_season",
            "conditions": "is_going_to_do_animate_new_season",
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
            "source": ["new_movie", "hot_movie", "movie_leaderboard", "movie_news", "do_search_movie"],
            "dest": "movie_lobby",
        },
        # 按下返回動畫選單
        {
            "trigger": "advance",
            "source": "animate_new_season",
            "dest": "animation_lobby",
            "conditions": "is_going_to_animation_lobby",
        },
        # 無條件返回 animate_new_season
        {
            "trigger": "go_back_animate_new_season",
            "source": "do_animate_new_season",
            "dest": "animate_new_season",
        },
    ],
    "initial" : "main_menu",
    "auto_transitions" : "False",
    "show_conditions" : "True",
}