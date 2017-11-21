#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import urllib2
import requests
import random
import time

from datetime import datetime, timedelta
from data_middleware import DataMiddleware

class NewsExtraction(object):

    def __init__(self):
        self.api_url = 'http://api.ruyi.ai/v1/message?app_key=0df50fac-4df0-466c-9798-99136f42bb8c&user_id={}&q={}'
        self.get_data = DataMiddleware()
        self.ruyiapi_rate = 50/60


    def call_api(self, sentence):
        """ ruyi-API limitation 50/60s
        """
        if not hasattr(self, '_begin'):
            setattr(self, '_begin', time.time())
        if not hasattr(self, '_count'):
            setattr(self, '_count', 0)

        rate = self._count / (time.time() - self._begin)
        if rate >= self.ruyiapi_rate:
            count_diff = self._count - (time.time() - self._begin) * self.ruyiapi_rate
            time.sleep(count_diff * self.ruyiapi_rate)

        url = self.api_url.format(str(random.random())[2:], urllib2.quote(sentence))
        ret = requests.get(url)
#        print( json.dumps( ret.json(), ensure_ascii=False, indent=True) )
        self._count += 1
        return ret.json()


    def read_all_from_db(self):
        signals = []
        for news in self.get_data.get_all_news():
            signal = self.parse(news)
            if signal:
                signals.append(signal)
            if len(signals) > 10:
                self.get_data.insert_signals(signals)
                signals = []
        if len(signals) > 0:
            self.get_data.insert_signals(signals)


    def read_latest_from_db(self, days_before=2):
        signals = []
        for news in self.get_data.get_latest_news(days_before):
            signal = self.parse(news)
            if signal:
                signals.append(signal)
            if len(signals) > 10:
                self.get_data.insert_signals(signals)
                signals = []
        if len(signals) > 0:
            self.get_data.insert_signals(signals)


    def parse(self, news):
        signal = {}

        for item in news[u'claims']:
            if item[u'p'] == u'标题':
                signal['title'] = item[u'o']
                ret = self.call_api(item[u'o'].encode('utf-8'))
                try:
                    intent = ret['result']['intents'][0]
                except:
                    print(ret)
                    continue
                if intent['is_match'] == 0:
                    return {}

                parameters = intent['parameters']
                if 'materials' in parameters:
                    signal['materials'] = parameters['materials'] if isinstance(parameters['materials'], list) else [parameters['materials']]
                if 'pricetrend' in parameters:
                    signal['price_trend'] = parameters['pricetrend']
                if 'bigevent' in parameters:
                    signal['strong_signals'] = [parameters['bigevent']]
                if 'normalevent' in parameters:
                    signal['normal_signals'] = [parameters['normalevent']]
                if 'location' in parameters:
                    signal['location'] = [parameters['location']]
                elif 'markets' in parameters:
                    signal['location'] = [parameters['markets']]

            elif item[u'p'] == u'日期':
                signal['news_time'] = item[u'o']
            elif item[u'p'] == u'正文':
                signal['content'] = item[u'o'].strip()
            else:
                pass

        signal['source'] = news['source']
        signal['extraction_version'] = 0.1
        signal['createdTime'] = datetime.utcnow().isoformat()
        signal['updatedTime'] = datetime.utcnow().isoformat()

        return signal


if __name__ == '__main__':
    obj = NewsExtraction()
    obj.read_all_from_db()
