#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from hzlib.libfile import readExcel2
import jieba
import random
import numpy as np
from sklearn import svm

TAB_WORDS = [
    u'价格暴涨重大新闻词库',
    u'价格暴跌重大新闻词库', 
    u'价格正常波动新闻词库',
    u'价格无影响新闻词库',
    u'价格影响不确定新闻词库',
]

DATA_SET = [
    u'训练数据集',
    u'测试数据集',
]

CLASS = [
    u'价格暴涨重大新闻',
    u'价格暴跌重大新闻',
    u'价格正常波动新闻',
    u'价格无影响新闻',
    u'价格影响不确定新闻',
]

content = readExcel2('/Users/bishop/Documents/海知智能/H大脑/重大新闻事件实现数据源_zhou20161206.xlsx')

def read_lexicon():
    """ {'价格暴涨重大新闻词库': ['暴涨', '产新扫尾', '价涨', ...], }
    """
    lexicon = {}
    for k, v in content['data'].iteritems():
        if k in TAB_WORDS:
            lexicon[k] = set()
            for i in v:
                lexicon[k].update(i.popitem())
    return lexicon


def read_data():
    """ [['连翘简介及鉴别方法', '价格无影响新闻'], ...]
    """
#    for k, v in content['fields'].iteritems():
#        if k in DATA_SET:
#            title_idx = v.index(u'新闻标题')
#            classify_idx = v.index(u'新闻分类')
#
    datas = []
    for k, v in content['data'].iteritems():
        if k in DATA_SET:
            for item in v:
                data = [None, None]
                for i, j in item.iteritems():
                    if i == u'新闻标题':
                        data[0] = j
                    elif i == u'新闻分类':
                        data[1] = j
                if data[1] is not None and data[1].strip() != u'':
                    datas.append(data)

    return datas


def main():
    lexicon = read_lexicon()
    for k, v in lexicon.iteritems():
        [jieba.add_word(word) for word in v]

    datas = read_data()
    X, Y = [], []
    for i in datas:
        matrix = [0, 0, 0, 0, 0]

        for j in jieba.cut(i[0], HMM=False):
            for idx in range(len(TAB_WORDS)):
                if j in lexicon[TAB_WORDS[idx]]:
                    matrix[idx] += 1
        X.append(matrix)
        Y.append(CLASS.index(i[1]))

    tenfold(X, Y)

def tenfold(X, Y):
    length = len(Y)
    index_list = range(length)
    errors = []

    for i in range(10):
        random.shuffle(index_list)
        x_train, x_test = [], []
        y_train, y_test = [], []

        for j in range(length):
            if j < 0.9 * length:
                x_train.append(X[index_list[j]])
                y_train.append(Y[index_list[j]])
            else:
                x_test.append(X[index_list[j]])
                y_test.append(Y[index_list[j]])

        clf = svm.LinearSVC()
        clf.fit(x_train, y_train) 
        y = clf.predict(x_test)
        error_count = np.nonzero(y != np.asarray(y_test))[0].shape[0]
        errors.append(error_count)
    print( sum(errors) / (10 * length) * 100 )


if __name__ == '__main__':
    main()
