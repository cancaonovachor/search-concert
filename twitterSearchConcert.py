import tweepy
import spacy
import datetime
import re
from dotenv import load_dotenv
import os
from os.path import join, dirname

# TODO:
# ・日付指定できるようにする。
# ・すでに終了しているものは弾く
# ・過去に開催したもので、月日だけのTweetはご検知される可能性あり、過去表現を形態素解析するなりして弾きたい
# ex)４月８日開催された演奏会のCDを以下サイトで販売しています。
# ・複数Dateが検出されると、日付を誤る恐れがある。（特に先に開催日でないものが記載されると）
# ex)１１月８日チケット販売開始！１２月８日演奏会を開催します。
# ・Googleカレンダーに自動追加（同じものをどう検知するか？アカウントと日付の一致？）
# ・新しいイベントのTweet、直近のイベントのTweet
# ・「合唱 演奏会 開催」と記入されていないものや日付がなかったり不完全なもの（2021/11開催予定）などは検知されないので、
# ハッシュタグで検知する機能の追加、もしくはフォローしていると「演奏会 開催」だけで検知
# ・開催地の検知

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CK = os.environ.get("CK")
CKS = os.environ.get("CKS")
AT = os.environ.get("AT")
ATS = os.environ.get("ATS")

auth = tweepy.OAuthHandler(CK, CKS)
auth.set_access_token(AT, ATS)
api = tweepy.API(auth)

nlp = spacy.load('ja_ginza')

def convDate(dateStr):
    dateNum = re.sub("\\D", "/", dateStr)
    dateList = dateNum.split("/")
    dateList = [a for a in dateList if a != '']
    dt_now = datetime.datetime.now()
    if ((len(dateList) != 2) & (len(dateList) != 3)):
        #print("debug1")
        return 0
    elif len(dateList) == 3: #2021/11/8
        #print("debug2")
        return datetime.datetime(int(dateList[0]), int(dateList[1]), int(dateList[2]))
    elif (len(dateList) == 2) & ((int(dateList[0]) <= 12) & (int(dateList[0]) >= 1)): #11/8
        #print("debug3 {} {}".format(int(dateList[0]),int(dateList[1])))
        return datetime.datetime(dt_now.year, int(dateList[0]), int(dateList[1]))
    else:
        #print("debug4 {} {}".format(int(dateList[0]),int(dateList[1])))
        return 0

tweets = tweepy.Cursor(api.search_tweets, q='合唱 演奏会 開催 exclude:retweets',
                           include_entities = True,
                           tweet_mode = 'extended',
                           lang = 'ja').items(10)

for tweet_json in tweets:
    tweet = tweet_json._json
    doc = nlp(tweet['full_text'])
    for ent in doc.ents:
        if ent.label_ == 'Date':
            #print(tweet['full_text'])
            #print(ent.text, ent.start_char, ent.end_char, ent.label_)
            date = convDate(ent.text)
            if date != 0:
                print(tweet['user']['name'], date.strftime("%Y/%m/%d"), "https://twitter.com/user/status/{}".format(tweet['id']))
            #else:
                #print("date undefined {}".format(ent.text))
            break
# 合唱団(twitterアカウント名)、日付、(場所)、origin_url

