#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from pymongo import MongoClient
from datetime import datetime, timedelta

class DataMiddleware(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.news_collection = client['kgbrain']['news']
        self.signal = client['kgbrain']['signal']
        self.entities_collection = client['kgbrain']['entities']


    def get_all_news(self):
        for news in self.news_collection.find(no_cursor_timeout=True):
            yield news

    def get_latest_news(self, days_before=2):
        min_time = datetime.today() - timedelta(days=days_before)
        for news in self.news_collection.find({'createdTime': {'$gt': min_time}}):
            yield news

    def insert_signals(self, signals):
        self.signal.insert_many(signals)
