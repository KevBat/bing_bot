#!/usr/bin/env python3

import requests
import json
import os
import random
import argparse
import logging
import logging.handlers as handlers

from time import sleep

class Configuration(dict):
    def __init__(self, *args):
        super(Configuration, self).__init__()

        for arg in args:
            for key, value in arg.items():
                value = Configuration(value) if isinstance(value, dict) else value
                self.__setattr__(key, value)

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key,value)

    def __setitem__(self, key, value):
        super(Configuration, self).__setitem__(key, value)
        self.__dict__.update({key: value})

class BingBot:
    def __init__(self, mobile_mode=False, custom_conf=None):        
        self.mobile_mode = mobile_mode
        self.custom_conf = custom_conf
        self.pyDir = os.path.dirname(__file__)
        self.readConfig()
        self.readUserAgent()
        self.readCookie()
        self.setupLogger()

    def printBanner(self):
        self.logger.info("===============================================")
        self.logger.info("    ____  _____   ________   ____  ____  ______")
        self.logger.info("   / __ )/  _/ | / / ____/  / __ )/ __ \/_  __/")
        self.logger.info("  / __  |/ //  |/ / / __   / __  / / / / / /")
        self.logger.info(" / /_/ // // /|  / /_/ /  / /_/ / /_/ / / /")
        self.logger.info("/_____/___/_/ |_/\____/  /_____/\____/ /_/")
        self.logger.info("The Bot that Bing's, so you don't have to...")
        self.logger.info("===============================================")
        self.logger.info("Mobile Option: " + str(self.mobile_mode))
        self.logger.info("Custom Config: " + str(self.custom_conf))
        self.logger.info("===============================================")

    def setupLogger(self):
        self.logger = logging.getLogger('bing_bot')
        self.logger.setLevel(logging.INFO)
        logHandler = handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10000,
            backupCount=2
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logHandler.setFormatter(formatter)
        self.logger.addHandler(logHandler)

    def readConfig(self):
        if self.custom_conf:
            configPath = self.custom_conf
        else:
            configPath = os.path.join(self.pyDir, '../conf/default_conf.json')
        with open(configPath, 'r') as f:
            configJson = Configuration(json.loads(f.read()))

        conf = Configuration(configJson)
        
        self.min_seconds = int(conf.min_seconds_between_searches)
        self.max_seconds = int(conf.max_seconds_between_searches)
        self.min_searches = int(conf.min_amount_of_searches_to_run)
        self.max_searches = int(conf.max_amount_of_searches_to_run)
        self.log_file = conf.log_file_path
        self.random_words_repo = conf.random_words_repo

    def readUserAgent(self):
        if self.mobile_mode:
            agentPath = os.path.join(self.pyDir, '../conf/user_agent_mobile.txt')
        else:
            agentPath = os.path.join(self.pyDir, '../conf/user_agent_edge.txt')
        with open(agentPath, 'r') as file:
            self.agent = file.read().replace('\n','')

    def readCookie(self):
        cookiePath = os.path.join(self.pyDir, '../conf/cookie.txt')
        with open(cookiePath, 'r') as file:
            self.cookie = file.read().replace('\n','')

    def generateRandomWord(self):
        try: 
            response = requests.get(self.random_words_repo)
            data = response.json()
        except requests.exceptions.HTTPError as err:
            self.logger.error("Error getting word json!", exc_info=True)
        random_key = random.choice(list(data.keys()))
        random_value = data[random_key]
        return random.choice(random_value)

    def run(self):
        self.printBanner()
        for i in range(random.randint(self.min_searches,self.max_searches)):
            query = self.generateRandomWord()
            cookies = {'required_cookie': self.cookie}
            headers = {'User-Agent': self.agent}
            url = "https://www.bing.com/search?q=" + query
            try:
                self.logger.info("GET " + url)
                response = requests.get(
                    url, 
                    cookies=cookies, 
                    headers=headers
                )
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                self.logger.error("Error submitting search request!", exc_info=True)
            sleep(random.randint(self.min_seconds,self.max_seconds))

        self.logger.info("BING BOT COMPLETE")

def main(args):
    bingBot = BingBot(mobile_mode=args.mobile, custom_conf=args.config)
    bingBot.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Query Bing search")
    parser.add_argument(
        '-c',
        '--config',
        help="Start up the bing_bot with custom config",
        type=str
    )
    parser.add_argument(
        '-m',
        '--mobile',
        action='store_true',
        help="Start up the bing_bot in mobile mode"
    )
    args = parser.parse_args()
    main(args)