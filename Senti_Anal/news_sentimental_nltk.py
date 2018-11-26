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


def clean_summary(summary):
    """Cleaning the news summary"""
    return ' '.join(re.sub("([^0-9A-Za-z])|(\w+:\/\/\S+)", " ", summary).split())


def analyze_sentiment(summary):
    """Analyze the news sentiments"""
    sent_analyzer = SentimentIntensityAnalyzer()
    polarity_score = sent_analyzer.polarity_scores(clean_summary(summary))
    score = polarity_score.get(COMPOUND)
    if score > 0:
        return 1
    elif score < 0:
        return -1
    else:
        return 0


def get_neg(index, value):
    """Second layer of identifing the negative sents """
    if -1 == value.SA_S or -1 == value.SA_H:
        return -1
    elif 0 == value.SA_S or 0 == value.SA_H:
        return 0
    else:
        for key in keywords:
            key = key.lower()
            if key in value.Headline.lower():
                return -1
            elif key in value.Summary.lower():
                return -1
        return 1


def get_keywords():
    """Read the keywords.csv, keep Negative sents/words"""
    try:
        keywords = pd.read_csv('keywords.csv')
        return keywords.Keywords.values.tolist()
    except FileNotFoundError as e:
        print(e)


if __name__ == "__main__":
    data = pd.read_excel('data.xlsx')
    # Columns are: Date, Date Published, Headline, Keyword, Summary, URL
    data['SA_S'] = np.array([analyze_sentiment(summary) for summary in data.Summary])
    data['SA_H'] = np.array([analyze_sentiment(headline) for headline in data.Headline])
    keywords = get_keywords()
    data['SA']  = np.array([get_neg(index, value) for index, value in data.iterrows()])
    data.drop(columns=['SA_S', 'SA_H'], inplace=True)
    data.to_csv('.csv', index=False)
