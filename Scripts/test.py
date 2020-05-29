import pandas as pd
from bert_sa import getPrediction
import mysql.connector
from mtranslate import translate
import tweepy 
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
import re
import nltk
from nltk.corpus import wordnet
import urllib
from rake_nltk import Rake
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
consumer_key=""
consumer_secret=""
access_key = ""
access_secret = ""
exclude_keywords=[]
mydb = mysql.connector.connect(host="localhost",user="sfadmin",passwd="7@3xyeR6x%uNAcy",database="nlp_engine")
mycursor = mydb.cursor()
mycursor.execute("SELECT * from Twitter_API")
records = mycursor.fetchall()
for single_record in records:
    consumer_key = single_record[2]
    consumer_secret = single_record[3]
    access_key = single_record[4]
    access_secret = single_record[5]
    break
mycursor.execute("SELECT * from Exclude_Keyword")
records_keywords = mycursor.fetchall()
for keywords in records_keywords:
    exclude_keywords.append(keywords[1])
# consumer_key = "Pywlk64OFS82OtOWIJuBKjPEW"
# consumer_secret = "Ql3Cb53gSsx6UWxdRfWyB0rnorlX8j9psdJ1T4bwo6ssPz6vrz"
# access_key = "332760146-dcUzpvnmz8i1XKHm8cTpfvG51mXJ8IaPNK5e3ytf"
# access_secret = "ZwwmWA8KgNJXjrlg9VZ5gfOd5EHLnistFi1OQNMODo1mB"
df=pd.read_excel("../Resources/DataSources2.xlsx")
Column=["organization","URL","twitter"]
df.columns=Column
df=df.replace(to_replace="?",value="NaN")
df=df.dropna()
df=df.drop(df[df["twitter"]=="NaN"].index)
df=df.reset_index(drop=True)
l=len(df["twitter"])
#print(df["twitter"])


##################################################################################################################        
# def sentiment_scores(sentence): 
  
#     # Create a SentimentIntensityAnalyzer object. 
#     sid_obj = SentimentIntensityAnalyzer()
    
  
#     # polarity_scores method of SentimentIntensityAnalyzer 
#     # oject gives a sentiment dictionary. 
#     # which contains pos, neg, neu, and compound scores. 
#     sentiment_dict = sid_obj.polarity_scores(sentence) 
      
#     print("Overall sentiment dictionary is : ", sentiment_dict) 
#     #print("sentence was rated as ", sentiment_dict['neg']*100, "% Negative") 
#     #print("sentence was rated as ", sentiment_dict['neu']*100, "% Neutral") 
#     #print("sentence was rated as ", sentiment_dict['pos']*100, "% Positive") 
  
#     print("Sentence Overall Rated As", end = " ") 
#     analysis = ""
#     # decide sentiment as positive, negative and neutral 
#     if sentiment_dict['compound'] >= 0.05 : 
#         analysis = "Positive"
  
#     elif sentiment_dict['compound'] <= - 0.05 : 
#         analysis = "Negative" 
  
#     else : 
#         analysis = "Neutral"
        
#     return sentiment_dict['pos']*100,sentiment_dict['neg']*100,sentiment_dict['neu']*100,analysis

for i in range(l):
    try:
        df["twitter"][i]=df["twitter"][i].split('/')[3]
    except (Exception) as e:
        pass

########################################################################################################################
def get_tweets(username):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    tweets = api.user_timeline(screen_name=username,count=5,tweet_mode="extended")


    tweets_for_csv = [tweet for tweet in tweets]
    
    for j in tweets_for_csv:
        temp_var=0
        trans=translate(j.full_text)
        if (len(exclude_keywords)>0):
            for words in exclude_keywords:
                if (trans.find(words) != -1):
                    temp_var=1
        if (temp_var==1):
            continue
        #pos,neg,neu,analysis = sentiment_scores(trans)
        prediction_sentence = ["", trans]
        prediction=getPrediction(tuple(prediction_sentence))
        analysis=prediction[1][2]
        hasht=j.entities['hashtags']
        hashTags = ''
        for c in hasht:
            hashTags = hashTags+c['text']+','
        hashTags=translate(hashTags)

        ENGAGEMENT_PARAMETER="FALSE"
        if(j.favorite_count>1 and j.retweet_count>1):
            ENGAGEMENT_PARAMETER="TRUE"
        #final_parameter='None'
        # credibility,parameter=credibility_score(trans)
        # if(parameter!=None):
        # 	final_parameter=' '.join([w for w in parameter])
        sql = "INSERT INTO tweet_entries (TIME_STAMP,ID,USER_NAME,TWEET,FOLLOWER_COUNT,LIKES,RETWEET_COUNT,ANALYSIS,DESCRIPTION,STATUSES_COUNT,FRIENDS_COUNT,FAVOURITES_COUNT,HASHTAGS,LOCATION,PROFILE_PICTURE,ENGAGEMENT_PARAMETER) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val = (j.created_at,j.id,username,j.full_text,j.user.followers_count,j.favorite_count,j.retweet_count,analysis,j.user.description,j.user.statuses_count,j.user.friends_count,j.user.favourites_count,hashTags,j.user.location,j.user.profile_image_url,ENGAGEMENT_PARAMETER)
        mycursor.execute(sql,val)
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")
    


if __name__ == '__main__':
    for i in range(0,l):
        register=df["twitter"][i]
        try:
        	get_tweets(register)
        except:
        	continue
