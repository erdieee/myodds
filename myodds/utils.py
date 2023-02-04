import json
from typing import Any, Dict, List


def load_config() -> Dict[str, Any]:
    """
    Load config file and returns is as a dictionary
    :return: Configuration dictionary
    """
    with open("config.json") as json_data:
        config = json.load(json_data)
        return config


def get_3_way_data(
    date: str,
    sport: str,
    division: str,
    game_time: str,
    teams: List[str],
    odds: List[str],
    images: List[str],
    url: str,
) -> Dict[str, Any]:
    """
    Gets all necessary scraped data for a sport which has
    home, draw and away odds and returns it as a dictionary
    :param date: Date when the game is played
    :param sport: Type of sport
    :param division: Sub divison of the sport
    :param game_time: Time when the game is played
    :param teams: List containing the best books
    :param odds: List containing the odds from the different books
    :param url: Url where the data is scraped from
    :return: Dictionary containing scraped data
    """
    return {
        "date": date,
        "sport": sport.title(),
        "sport_subdivision": division,
        "play_time": game_time,
        "team1": teams[0].text,
        "team2": teams[1].text,
        "home_odds": float(odds[0].text),
        "draw_odds": float(odds[1].text),
        "away_odds": float(odds[2].text),
        "home_book": images[0]["alt"],
        "draw_book": images[1]["alt"],
        "away_book": images[2]["alt"],
        "data_source": url,
    }


def get_2_way_data(
    date: str,
    sport: str,
    division: str,
    game_time: str,
    teams: List[str],
    odds: List[str],
    images: List[str],
    url: str,
) -> Dict[str, Any]:
    """
    Gets all necessary scraped data for a sport which has
    home, draw and away odds and returns it as a dictionary
    :param date: Date when the game is played
    :param sport: Type of sport
    :param division: Sub divison of the sport
    :param game_time: Time when the game is played
    :param teams: List containing the best books
    :param odds: List containing the odds from the different books
    :param url: Url where the data is scraped from
    :return: Dictionary containing scraped data
    """
    return {
        "date": date,
        "sport": sport.title(),
        "sport_subdivision": division,
        "play_time": game_time,
        "team1": teams[0].text,
        "team2": teams[1].text,
        "home_odds": float(odds[0].text),
        "draw_odds": None,
        "away_odds": float(odds[-1].text),
        "home_book": images[0]["alt"],
        "draw_book": None,
        "away_book": images[-1]["alt"],
        "data_source": url,
    }
