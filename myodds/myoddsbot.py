import logging
from typing import Any, Dict

import pandas as pd

from myodds.analyzer import Analyzer
from myodds.constants import BetType, SPORTS
from myodds.scraper import Scraper
from myodds.rpc import Telegram


logger = logging.getLogger(__name__)


class MyOddsBot:
    """ 
    Main bot class
    Runs all processed needed to find opportunities
    """

    def __init__(self, config) -> None:
        """
        Initialization of the bot
        :param config: COnfiguration dictionary
        :return: None
        """
        self._config = config
        self.scraper = Scraper(self._config)
        
        if self._config['telegram']['enabled']:
            self.telegram = Telegram(self._config)

    def process(self, sport, division, url) -> None:
        """
        Main process scrapes the data for a given sport and subdivision and checks 
        if there there is a opportunity
        :return: None
        """
        df = self.scraper.get_matches(sport, division, url)
        
        # check for surebet
        if self._config['check_sure_bet']:
            self.check_sure_bet(df)

    def runner(self) -> None:
        """
        Main loop goes over all sports and subdivision
        Checks if a proxy is used
        :return: None
        """
        try:
            self.scraper._get_browser_page()
        except:
            logger.warning('Could not create browser. Waiting for next iteration')
            self.scraper._stop_browser()
            return
        for sport, subdivision in SPORTS.items():
            for division, url in subdivision.items():
                try:
                    self.process(sport, division, url)
                except:
                    logger.warning(f'Could not process data for {sport}: {division}. Going to next..')
        self.scraper._stop_browser()
        

    def check_sure_bet(self, df: pd.DataFrame) -> None:
        """
        Check if there is a sure bet opportunity and calculates
        proposed bet amount
        :param df: Dataframe containing scraped data
        :return: None
        """
        df = Analyzer.check_is_sure_bet(df, self._config['min_win_perc'])
        df = Analyzer.get_credible_values(df, self._config['min_bet'], self._config['max_bet'])
        if df.empty:
            logger.info('No sure bet found. Waiting for next iteration')
            return
        logger.debug(df)
        self.prepare_send_message(df, BetType.SURE_BET)

    def prepare_send_message(self, df: pd.DataFrame, bet_type: BetType) -> None:
        """
        Prepare message to send to telegram
        proposed bet amount
        :param df: Dataframe containing scraped data with bets and amounts
        :param bet_type: Type of bet
        :return: None
        """
        sure_bets = []
        for index, row in df.iterrows():
            sure_bets.append(row.to_dict())
        for bet in sure_bets:
            logger.info(f'Found {str(bet_type)}: {bet}')
            if self._config['telegram']['enabled']:
                self.send_msg(bet, bet_type)

    def send_msg(self, bet: Dict[str, Any], bet_type: BetType) -> None:
        """
        Sends message to telegram
        :param bet: Bet as dictionary
        :param bet_type: Type of bet
        :return: None
        """
        self.telegram.send_message(bet, bet_type)