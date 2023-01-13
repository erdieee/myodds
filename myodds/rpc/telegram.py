import logging
from typing import Any, Dict

from telegram import ParseMode, Update
from telegram.error import NetworkError, TelegramError
from telegram.ext import CallbackContext, CommandHandler, Updater

from myodds.constants import BetType


logger = logging.getLogger(__name__)


class Telegram:
    """ 
    This class handles all telegram communication 
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Init the Telegram call
        :param config: Configuration object as dictionary
        :return: None
        """
        self._config = config
        self.token = self._config['telegram']['token']
        self.chat_id = self._config['telegram']['chat_id']
        self._updater = Updater(token=self.token, use_context=True)
        self._init()

    def _init(self) -> None:
        """
        Define all commands the bot can use
        :return: None
        """
        handles = [
            CommandHandler('start', self._start),
            CommandHandler('help', self._help),
            CommandHandler('version', self._version),
        ]

        for handle in handles:
            self._updater.dispatcher.add_handler(handle)

        self._updater.start_polling()

        logger.info(
            'rpc.telegram is listening for following commands: %s',
            [h.command for h in handles]
        )
    

    def _start(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /start.
        Sends start up message
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        self._send_message('Started bot')

    def _help(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /help.
        Send helper message
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        help_msg = (
            "*Bot usage:* \n"
            "*/start:* `Starts the bot`\n"
            "*/version:* `Show version of the bot`\n"
            "*/help:* `Show this help message`\n"
        )
        self._send_message(help_msg, parse_mode = ParseMode.MARKDOWN)

    def _version(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /version.
        Send current bot version
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        self._send_message(f'*MyOddsBot version:* {0.1}')

    def compose_sure_bet(self, bet: Dict[str, Any]) -> str:
        """
        Creates the message for a sure bet 
        :param bet: Dictionary that contains all bet details
        :return: Message string
        """
        bet['emoji'] = self._get_emoji(bet)
        bet['bet_type'] = str(bet['bet_type']).replace('_', ' ').title()

        message = (
            f"*{bet['bet_type']}* {bet['emoji']} \n"
            f"*Sport*: {bet['sport']} \n"
            f"*Sub Division*: {bet['sport_subdivision']} \n"
            f"*{bet['team1']}* vs *{bet['team2']}* \n"
            f"*On*: {bet['date']} *at* {bet['play_time']}\n"
            f"*Expected Win*: {bet['expected_win']:.2%} \n"
            f"*Home* \n"
            f"{''.join(' ' for _ in range(4))}*Book*: {bet['home_book']} \n"
            f"{''.join(' ' for _ in range(4))}*Odds*: `{bet['home_odds']}` \n"
            f"{''.join(' ' for _ in range(4))}*Invest Perc*: `{bet['invest_percentages'][0]:.2%}` \n"
            f"{''.join(' ' for _ in range(4))}*Invest Amount*: `{bet['invest_values'][0]}` \n"
            f"*Draw* \n"
            f"{''.join(' ' for _ in range(4))}*Book*: {bet['draw_book']} \n"
            f"{''.join(' ' for _ in range(4))}*Odds*: `{bet['draw_odds']}` \n"
            f"{''.join(' ' for _ in range(4))}*Invest Perc*: `{bet['invest_percentages'][1]:.2%}` \n"
            f"{''.join(' ' for _ in range(4))}*Invest Amount*: `{bet['invest_values'][1]}` \n"
            f"*Away* \n"
            f"{''.join(' ' for _ in range(4))}*Book*: {bet['away_book']} \n"
            f"{''.join(' ' for _ in range(4))}*Odds*: `{bet['away_odds']}` \n"
            f"{''.join(' ' for _ in range(4))}*Invest Perc*: `{bet['invest_percentages'][-1]:.2%}` \n"
            f"{''.join(' ' for _ in range(4))}*Invest Amount*: `{bet['invest_values'][-1]}` \n"
            f"*Data Source:* {bet['data_source']}"
        )
        return message

    def compose_positive_ev_bet(self, bet: Dict[str, Any]) -> str:
        """
        Creates the message for a positive ev bet
        :param bet: Dictionary that contains all bet details
        :return: Message string
        """
        pass

    def _get_emoji(self, bet: Dict[str, Any]) -> str:
        """
        Gets an emoji for respective bet and for expected win
        :param bet: Dictionary that contains all bet details
        :return: Emoji as string 
        """
        if bet['bet_type'] == BetType.SURE_BET:
            if float(bet['expected_win']) >= 5.0:
                 return "\N{ROCKET}"
            else:
                return "\N{WHITE HEAVY CHECK MARK}"
        if bet['bet_type'] == BetType.POSITIVE_EV_BET:
            return "\N{BAR CHART}"

    def send_message(self, bet: Dict[str, Any], bet_type: BetType) -> None:
        """
        Calls the respective compose message for bet_type
        :param bet: Dictionary that contains all bet details
        :param bet_type: Differenciates between the bet types
        :return: None
        """
        bet['bet_type'] = str(bet_type)
        if bet_type is BetType.SURE_BET:
            msg = self.compose_sure_bet(bet)
        if bet_type is BetType.POSITIVE_EV_BET:
            msg = self.compose_positive_ev_bet(bet)

        self._send_message(msg.replace('_', '')) #replace needed because can't parse underscore
        

    def _send_message(self, message: str, parse_mode: str = ParseMode.MARKDOWN) -> None:
        """
        Send given message
        :param message: message
        :param parse_mode: telegram parse mode
        :return: None
        """
        try:
            try:
                self._updater.bot.send_message(
                    chat_id = self.chat_id,
                    text = message,
                    parse_mode = parse_mode  
                )
            except NetworkError as network_err:
                # Sometimes the telegram server resets the current connection,
                # if this is the case we send the message again.
                logger.warning(
                    f'TelegramError: {network_err.message}! Trying one more time.'
                )
                self._updater.bot.send_message(
                    chat_id = self.chat_id,
                    text = message,
                    parse_mode = parse_mode 
                )
        except TelegramError as telegram_err:
            logger.warning(
                f'TelegramError: {telegram_err.message}! Giving up on that message.'
            )

