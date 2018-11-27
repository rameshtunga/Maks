# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 11:32:32 2018

@author: kumadee
"""

# -*- coding: utf-8 -*-
"""
@description: this module will add a new column called 'SA', sentimental
value will be stored, like 0: nuetral, >0: Positive, <0: Negative
@author: kumadee
"""
import pandas as pd
import numpy as np
import re

from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

COMPOUND = 'compound'
REEXP = "([^0-9A-Za-z])|(\w+:\/\/\S+)"
KEYWORDSFILE = 'keywords.csv'


class SentimentAnalysis(object):
    def __init__(self, filename):
        self.filename = filename
        self.file, self.ext = self._split_filename()
        self.keywords = SentimentAnalysis._get_keywords()
        self.data = self._read_file()

    def _split_filename(self):
        if '.' in self.filename:
            file, ext = self.filename.split('.')
            return file, ext
        raise KeyError()

    def _read_file(self):
        try:
            if 'csv' in self.ext:
                return pd.read_csv(self.filename)
            elif 'xls' in self.ext:
                return pd.read_excel(self.filename)
        except FileNotFoundError:
            raise FileNotFoundError()

    @staticmethod
    def _clean_summary(summary):
        """Cleaning the news summary"""
        return ' '.join(re.sub(REEXP, " ", summary).split())

    def _analyze_sentiment(self, summary):
        """Analyze the news sentiments"""
        sent_analyzer = SentimentIntensityAnalyzer()
        polarity_score = sent_analyzer.polarity_scores(SentimentAnalysis._clean_summary(summary))
        score = polarity_score.get(COMPOUND)
        if score > 0:
            return 1
        elif score < 0:
            return -1
        else:
            return 0

    def _get_neg(self, index, value):
        """Second layer of identifing the negative sents """
        if -1 == value.SA_S or -1 == value.SA_H:
            return -1
        elif 0 == value.SA_S or 0 == value.SA_H:
            return 0
        else:
            for key in self.keywords:
                key = key.lower()
                if key in value.Headline.lower():
                    return -1
                elif key in value.Summary.lower():
                    return -1
            return 1

    @staticmethod
    def _get_keywords():
        """Read the keywords.csv, keep Negative sents/words"""
        try:
            keywords = pd.read_csv(KEYWORDSFILE)
            return keywords.Keywords.values.tolist()
        except FileNotFoundError as e:
            print(e)

    def analyzer(self):
        self.data['SA_S'] = np.array([self._analyze_sentiment(summary) for summary in self.data.Summary])
        self.data['SA_H'] = np.array([self._analyze_sentiment(headline) for headline in self.data.Headline])
        self.data['SA'] = np.array([self._get_neg(index, value) for index, value in self.data.iterrows()])
        self.data.drop(columns=['SA_S', 'SA_H'], inplace=True)
        self._write_file(self.data)

    def _write_file(self, data):
        if 'csv' in self.ext:
            data.to_csv(self.file+'%s.csv' % '_sent')
        elif 'xls' in self.ext:
            data.to_excel(self.file+'%s.xlsx' % '_sent')


if __name__ == "__main__":
    pass

############# How to Use ###############
# obj = SentimentAnalysis('data.xlsx')
# obj.analyzer()
########################################

