# MyOdds (Sure Bet/Arbitrage Bet)
Finds sure bets (arbitrage bets) finder
Scrape https://www.oddschecker.com/ and check for sure bets and send a notification to telegram.

## Quick start
### Software requirements

- [Python >= 3.8](http://docs.python-guide.org/en/latest/starting/installation/)
- [pip](https://pip.pypa.io/en/stable/installing/)
- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Installation
A setup script is provided for easy installation. It is a easy as running
```
git clone https://github.com/erdieee/myodds.git

# Enter downloaded directory
cd myodds

# --install, Install myodds from scratch
./setup.sh -i
```
To update to new changes in the future run
```
# --update
./setup.sh -u
```

### Configuration

After setup.sh is run, you will find a config.json file in your root directory. Change the config based on your needs.

### Run the script
Whenever you want to run the script you need to activate the virtual enviroment first.
```
# activate your virtual enviroment (in Windows: .env/Scripts/activate.bat)
source .env/bin/activate
# run it
myodds
```

### Telegram

If a sure bet is found you can send a notification to telegram. The bet will be shown in the following format
![Telegram](assets/telegram-preview.png)