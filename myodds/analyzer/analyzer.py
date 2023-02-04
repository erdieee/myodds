import logging
from typing import List

import numpy as np
import pandas as pd

from myodds.constants import COLUMNS, INVEST_AMOUNT_DECIMALS


logger = logging.getLogger(__name__)


class Analyzer:
    """
    Class to analyze if there is an opportunity and calculate the
    respective investments and wins
    """

    @staticmethod
    def check_is_sure_bet(df: pd.DataFrame, min_win_perc: float) -> pd.DataFrame:
        """
        Goes over the rows of the dataframe and checks if there is a sure bet
        :param df: Dataframe containing all data
        :param min_win_perc: Minium win percentage that the user want to be achived for considering the bet
        :return: Dataframe with check for sure bet with respective invest percentages of the portfolio
        """
        cols = [col for col in COLUMNS if "odds" in col]
        odds = df[cols].to_numpy()
        reciprocal: List = []
        sure_bets: List = []
        invest: List = []
        for bet in odds:
            odds_cost = 1 / bet
            # Transform this cost to a percentage (The percentage that should be invested at each option)
            odd_percentage = odds_cost / np.sum(odds_cost)
            # Calculate the cost of the bet (The money that would cost to win an euro) [If positive it is a sure bet]
            total_euro_cost = 1 - np.sum(odds_cost) - min_win_perc
            reciprocal.append(np.round(np.sum(odds_cost), 5))
            if total_euro_cost > 0:
                sure_bets.append(True)
                invest.append(list(np.round(odd_percentage, 4)))
            else:
                sure_bets.append(False)
                invest.append(0)
        df["reciprocal"] = reciprocal
        df["is_sure_bet"] = sure_bets
        df["invest_percentages"] = invest
        logger.info(df)
        return df

    @staticmethod
    def get_credible_values(
        df: pd.DataFrame, min_bet: float, max_bet: float
    ) -> pd.DataFrame:
        """
        Only checks rows of dataframe where sure bet is true and
        calculates creadible values to invest to not become suspicious
        :param df: Dataframe containing all data
        :param min_bet: Minium investing sum amount
        :param max_bet: Maximum investing sum amount
        :return: Dataframe containing the recommended investment amounts and expected wins
        """
        df = df.copy()
        df = df[df["is_sure_bet"] == True]
        vals = df["invest_percentages"].to_numpy()
        invest: List = []
        for values in vals:
            all_posible_bets = np.arange(start=min_bet, stop=max_bet, step=0.01)
            all_posible_bets = np.repeat(all_posible_bets, len(values)).reshape(
                -1, len(values)
            )
            values = (
                np.repeat(a=values, repeats=len(all_posible_bets))
                .reshape(len(values), -1)
                .T
            )
            possible_invests = values * all_posible_bets
            possible_rounded_invests = np.round(
                possible_invests, INVEST_AMOUNT_DECIMALS
            )
            losses = np.sum(np.abs(possible_rounded_invests - possible_invests), axis=1)
            best_invest = possible_rounded_invests[np.argmin(losses)]
            invest.append(best_invest.tolist())  # to list only for testing
        df["invest_values"] = invest
        df["expected_win"] = np.round((1 - df["reciprocal"]), 5)
        return df
