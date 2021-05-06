#! usr/bin/env python3
import praw
import os
import random
import webbrowser
import pandas as pd
import datetime as dt
from tinydb import TinyDB, Query
from nltk import tokenize
from operator import itemgetter
import math
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
stop_words = set(stopwords.words('english'))

db = TinyDB('db.json', storage=CachingMiddleware(JSONStorage))
reddit = praw.Reddit(client_id='14 char string',
                     client_secret='secret',
                     user_agent='app name',
                     username='reddit uname',
                     password='reddit password')


def get_top_n(dict_elem, n):
    result = dict(sorted(dict_elem.items(),
                  key=itemgetter(1), reverse=True)[:n])
    return result


def check_sent(word, sentences):
    final = [all([w in x for w in word]) for x in sentences]
    sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
    return int(len(sent_len))


def scrape_top(sub="News", n=5):
    try:
        count = 0
        step = int(n / 100)
        print(step)
        subreddit = reddit.subreddit(sub)

        for submission in subreddit.top(limit=n):
            count = count + 1
            if count == step:
                print('.', end='')
                count = 0
            text = submission.title.split()
            total_word_length = len(text)

            tf_score = {}
            for each_word in text:
                each_word = each_word.replace('.', '')
                if each_word not in stop_words:
                    if each_word in tf_score:
                        tf_score[each_word] += 1
                    else:
                        tf_score[each_word] = 1

            # Dividing by total_word_length for each dictionary element
            tf_score.update((x, y/int(total_word_length))
                            for x, y in tf_score.items())

            total_sentences = tokenize.sent_tokenize(submission.title)
            total_sent_len = len(total_sentences)

            idf_score = {}
            for each_word in text:
                each_word = each_word.replace('.', '')
                if each_word not in stop_words:
                    if each_word in idf_score:
                        idf_score[each_word] = check_sent(
                            each_word, total_sentences)
                    else:
                        idf_score[each_word] = 1

            # Performing a log and divide
            idf_score.update((x, math.log(int(total_sent_len)/y))
                            for x, y in idf_score.items())

            tf_idf_score = {key: tf_score[key] *
                            idf_score.get(key, 0) for key in tf_score.keys()}

            Nkeywords = list(get_top_n(tf_idf_score, 3).keys())

            keywords = []
            for key in Nkeywords:
                keywords.append(key.lower().strip("!@#$$%^&*(){}|:<>?,./;'[]\[=-"))

            db.insert({'url': submission.url, 'keywords': keywords})
    except:
        pass


def scrape_new(sub="News", n=5):
    try:
        subreddit = reddit.subreddit(sub)

        for submission in subreddit.new(limit=n):
            text = submission.title.split()
            total_word_length = len(text)

            tf_score = {}
            for each_word in text:
                each_word = each_word.replace('.', '')
                if each_word not in stop_words:
                    if each_word in tf_score:
                        tf_score[each_word] += 1
                    else:
                        tf_score[each_word] = 1

            # Dividing by total_word_length for each dictionary element
            tf_score.update((x, y/int(total_word_length))
                            for x, y in tf_score.items())

            total_sentences = tokenize.sent_tokenize(submission.title)
            total_sent_len = len(total_sentences)

            idf_score = {}
            for each_word in text:
                each_word = each_word.replace('.', '')
                if each_word not in stop_words:
                    if each_word in idf_score:
                        idf_score[each_word] = check_sent(
                            each_word, total_sentences)
                    else:
                        idf_score[each_word] = 1

            # Performing a log and divide
            idf_score.update((x, math.log(int(total_sent_len)/y))
                            for x, y in idf_score.items())

            tf_idf_score = {key: tf_score[key] *
                            idf_score.get(key, 0) for key in tf_score.keys()}

            Nkeywords = list(get_top_n(tf_idf_score, 3).keys())

            keywords = []
            for key in Nkeywords:
                keywords.append(key.lower())

            db.insert({'url': submission.url, 'keywords': keywords})
    except:
        print('error')
        pass


def search(keyword: str):
    keysearch = Query()
    res = db.search(keysearch.keywords.any(keyword))
    for i in res:
        print(i['url'])


def search_list(keyword: str):
    keysearch = Query()
    res = db.search(keysearch.keywords.any(keyword))
    key = []
    for i in res:
        key.append(i['url'])
    return key


if __name__ == "__main__":
    while True:
        com = input('> ').lower()
        if com == "t":
            sub = input('subreddit? ')
            n = int(input('n? '))
            scrape_top(sub, n)
            continue

        if com == "n":
            sub = input('subreddit? ')
            n = int(input('n? '))
            scrape_new(sub, n)
            continue

        if com == 's':
            search(input('key? ').lower())
            continue

        if com == 'r':
            webbrowser.open(random.choice(search_list(input('key? ').lower())))
            continue
        
        if com == 'file':
            with open('tocrawl', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    scrape_new(line, 500)
                    print("New " + line)
                    scrape_new(line, 2000)
                    print("Top " + line)

        try:
            webbrowser.open(random.choice(search_list(com)))

        except IndexError:
            print("No entries")
