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
        "do_animate_new_season",
        "animate_leaderboard",
        "hot_animate",
        "animate_news",
        "search_animate",
        "do_search_animate",
        "add_favorite",
        "my_favorite",
        "show_favorite",
        "leave_favorite",
        "delete_favorite",
        "do_game"
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
            "source": "game_lobby",
            "dest": "do_game",
            "conditions": "is_going_to_do_game",
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
        # 從search movie 到 movie_lobby
        {
            "trigger": "advance_postback",
            "source": "search_movie",
            "dest": "movie_lobby",
            "conditions": "is_going_to_movie_lobby_postback",
        },
        # 加入我的最愛
        {
            "trigger": "advance_postback",
            "source": ["movie_lobby", "animate_new_season", "animation_lobby", "main_menu", "search_movie", "search_animate"],
            "dest": "add_favorite",
            "conditions": "is_going_to_add_favorite",
        },
        # 用 advance 我的最愛
        {
            "trigger": "advance",
            "source": ["main_menu", "movie_lobby", "animation_lobby", "search_movie", "animate_new_season", "search_animate"],
            "dest": "my_favorite",
            "conditions": "is_going_to_my_favorite",
        },
        # 用 advance_postback 我的最愛
        {
            "trigger": "advance_postback",
            "source": ["search_movie", "search_animate"],
            "dest": "my_favorite",
            "conditions": "is_going_to_my_favorite_postback",
        },
        # 看我的最愛
        {
            "trigger": "advance_postback",
            "source": "my_favorite",
            "dest": "show_favorite",
            "conditions": "is_going_to_show_favorite",
        },
        # 刪除最愛
        {
            "trigger": "advance_postback",
            "source": "show_favorite",
            "dest": "delete_favorite",
            "conditions": "is_going_to_delete_favorite",
        },
        # 無條件返回 看我的最愛
        {
            "trigger": "go_back_show_favorite",
            "source": "delete_favorite",
            "dest": "show_favorite",
        },
        # 返回 我的最愛
        {
            "trigger": "advance",
            "source": "show_favorite",
            "dest": "my_favorite",
            "conditions": "is_going_to_show_favorite_my",
        },
        # 離開 我的最愛
        {
            "trigger": "advance",
            "source": "my_favorite",
            "dest": "leave_favorite",
            "conditions": "is_going_to_leave_favorite",
        },
        {
            "trigger": "advance",
            "source": "animation_lobby",
            "dest": "animate_new_season",
            "conditions": "is_going_to_animate_new_season",
        },
        {
            "trigger": "advance_postback",
            "source": "animate_new_season",
            "dest": "do_animate_new_season",
            "conditions": "is_going_to_do_animate_new_season",
        },
        {
            "trigger": "advance",
            "source": "animation_lobby",
            "dest": "animate_leaderboard",
            "conditions": "is_going_to_animate_leaderboard",
        },
        {
            "trigger": "advance_postback",
            "source": "animation_lobby",
            "dest": "hot_animate",
            "conditions": "is_going_to_hot_animate",
        },
        {
            "trigger": "advance",
            "source": "animation_lobby",
            "dest": "animate_news",
            "conditions": "is_going_to_animate_news",
        },
        {
            "trigger": "advance",
            "source": "animation_lobby",
            "dest": "search_animate",
            "conditions": "is_going_to_search_animate",
        },
        {
            "trigger": "advance",
            "source": "search_animate",
            "dest": "do_search_animate",
        },
        # 從search_animate 到 animation_lobby
        {
            "trigger": "advance_postback",
            "source": "search_animate",
            "dest": "animation_lobby",
            "conditions": "is_going_to_animation_lobby_postback",
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
            "source": ["new_movie", "hot_movie", "movie_leaderboard", "movie_news", "do_search_movie", "add_favorite", "leave_favorite"],
            "dest": "movie_lobby",
        },
        # 按下返回 animation_lobby
        {
            "trigger": "advance",
            "source": "animate_new_season",
            "dest": "animation_lobby",
            "conditions": "is_going_to_animation_lobby",
        },
        # 無條件返回 animate_new_season
        {
            "trigger": "go_back_animate_new_season",
            "source": ["do_animate_new_season", "add_favorite", "leave_favorite"],
            "dest": "animate_new_season",
        },
        # 無條件返回 search_movie
        {
            "trigger": "go_back_search_movie",
            "source": "leave_favorite",
            "dest": "search_movie",
        },
        # 無條件返回 main_menu
        {
            "trigger": "go_back_main_menu",
            "source": "leave_favorite",
            "dest": "main_menu",
        },
        # 無條件返回 search_animate
        {
            "trigger": "go_back_search_animate",
            "source": "leave_favorite",
            "dest": "search_animate",
        },
        # 無條件返回 animation_lobby
        {
            "trigger": "go_back_animation_lobby",
            "source": ["animate_leaderboard", "hot_animate", "animate_news", "do_search_animate", "add_favorite", "leave_favorite"],
            "dest": "animation_lobby",
        },
        # 無條件返回 game_lobby
        {
            "trigger": "go_back_game_lobby",
            "source": "do_game",
            "dest": "game_lobby",
        }
    ],
    "initial" : "main_menu",
    "auto_transitions" : "False",
    "show_conditions" : "True",
}