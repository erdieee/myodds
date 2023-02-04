import logging
import time
from typing import Any, Dict

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Playwright

from myodds.constants import COLUMNS, DAY, DAYDATE, ODDS, PLAY_TIME, SPORT_INFO, TEAMS
from myodds.utils import get_2_way_data, get_3_way_data


logger = logging.getLogger(__name__)


class Scraper:
    """
    Class for scraping the data from https://www.oddschecker.com/it
    for a specific sport
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialization of class
        :param config: Configuration dictionary
        :return: None
        """
        self._config = config
        self._p: Any = None
        self._page: Any

    def _get_browser_page(self) -> None:
        """
        Open a browser which stays open until closed
        and sets a page that is used for scrolling
        It click on the page such that the location does not appear again
        and the matches can be scraped without problems
        :return: None
        """
        self._p = sync_playwright().start()
        if self._config["proxy"]["enabled"]:
            browser = self._p.firefox.launch(
                headless=self._config["headless"],
                proxy={"server": self._config["proxy"]["server"]},
            )
        else:
            browser = self._p.firefox.launch(headless=self._config["headless"])
        self._page = browser.new_page()
        self._page.goto(self._config["base_url"])
        self._page.wait_for_load_state("networkidle")
        self._page.locator("#om-bzoadzmqncddgwp3ksmq").click()
        self._page.wait_for_load_state("networkidle")

    def _stop_browser(self) -> None:
        """
        Closes the open browser which stayed open
        :return: None
        """
        if self._p is not None:
            self._p.stop()

    def _get_html(self, url: str) -> Any:
        """
        Grabs html from requested page
        :param url: Url that needs to bet scraped
        :return: Html of the page
        """
        page = self._page
        page.goto(url)
        for i in range(7):
            page.mouse.wheel(0, 1000)

        page.wait_for_load_state("networkidle")
        try:
            content = page.content()
        except:
            logger.warning(f"Could not retrive html from {url}. Retrying again")
            self._get_html(url)
        return content

    def get_matches(self, sport: str, division: str, url: str) -> pd.DataFrame:
        """
        Grab the data from the url for a given sport and
        returns it as a dataframe
        :param sport: Sport that needs to be scraped
        :param division: Sub division of the sport
        :param url: Url that needs to bet scraped
        :return: Dataframe with scraped data
        """
        logger.info(f"Getting matches for {sport}: {division}..")
        content = self._get_html(url)
        soup = BeautifulSoup(content, "html.parser")
        data = []

        for day in soup.find_all("ul", class_=DAY):
            date = day.find("div", class_=DAYDATE).text
            sport_info = day.find_all("div", class_=SPORT_INFO)
            play_time = day.find_all("div", class_=PLAY_TIME)
            for i, game in enumerate(sport_info):
                teams = game.find_all("div", class_=TEAMS)
                odds = game.find_all("div", class_=ODDS)
                game_time = play_time[i].text
                images = [image.find("img") for image in odds]
                try:
                    info = get_3_way_data(
                        date, sport, division, game_time, teams, odds, images, url
                    )
                    # still need to distinguish between 2 or 3 way and get game and subdivision beforehand
                    data.append(info)
                except Exception as e:
                    logger.warning(
                        f"Could not retrive data for {sport}: {division} on {date} "
                        f"for {teams[0].text} vs. {teams[1].text}. Exception {e}, skipping entry."
                    )
        df = pd.DataFrame(data, columns=COLUMNS)
        logger.debug(f"Scraped data: \n {df}")  # change to debug
        logger.info(f"Matches ready for {sport}: {division}")
        return df
