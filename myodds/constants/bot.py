"""
Constants which the bot needs to work
"""

from enum import Enum


class BetType(str, Enum):
    """
    Enum to distinguish between sure and positive ev bet
    """

    SURE_BET = "sure_bet"
    POSITIVE_EV_BET = "positive_ev_bet"

    def __str__(self):
        # explicitly convert to String to help with exporting data.
        return self.value


REFRESH_TIME_SECONDS = 300
INVEST_AMOUNT_DECIMALS = 1

COLUMNS = [
    "date",
    "play_time",
    "sport",
    "sport_subdivision",
    "data_source",
    "team1",
    "team2",
    "home_odds",
    "draw_odds",
    "away_odds",
    "home_book",
    "draw_book",
    "away_book",
    "reciprocal",
    "is_sure_bet",
    "expected_win",
    "invest_percentages",
    "invest_values",
]
