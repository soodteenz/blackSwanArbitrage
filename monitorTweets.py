# Imports 
import tweepy
import os
import telegram 
from schedule import every, repeat, run_pending
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import csv
import pandas as pd
import tweetAnalysis as ta

# GLOBAL VARIABLES
# LOADING .env 
load_dotenv(find_dotenv())

# Telegram Bot
telegramChatID = os.getenv("telegramChatID")
telegramToken = os.getenv("telegramToken")

# API KEYS
apiKey = os.getenv("apiKey")
apiKeySecret = os.getenv("apiKeySecret")
accessToken = os.getenv('accessToken')
accessTokenSecret = os.getenv('accessTokenSecret')

# BEARER TOKEN
bearerToken = os.getenv('bearerToken')
twitterAccount = os.getenv('user')
dbPath = os.getenv('dbPath')

# FUNCTIONS
def send(msg:str, chat_id, token):
    """
    Send a message to a telegram user or group specified on chatId
    chat_id must be a number!
    """
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)

# If the csv file doesn't exist
def fileDoesNotExist():
    print("CSV File Does Not Exist - CREATING")
    # assign header columns
    header = ['tweetAuthorID', 'tweetID', 'userTweet']
    # open CSV file and assign header
    with open(dbPath, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)

# Removes ALL whitespaces in the csv
def cleanup():
    df = pd.read_csv(dbPath)
    #checking the number of empty rows in th csv file
    print (df.isnull().sum())
    #Droping the empty rows
    modifiedDF = df.dropna()
    #Saving it to the csv file 
    modifiedDF.to_csv(dbPath,index=False)

# If the csv file exists
def fileDoesExist():
    # Login
    # API v2
    client = tweepy.Client(bearer_token=bearerToken)
    # API v1.1
    auth = tweepy.OAuth2BearerHandler(bearer_token=bearerToken)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # getting the clientID
    usertwitterAccount = api.get_user(screen_name=twitterAccount)
    print("Twitter Account ID:", usertwitterAccount.id)

    tweets = client.get_users_tweets(id=usertwitterAccount.id,end_time=datetime.today(),max_results=5)

    # gets the first latest tweet from a user
    for eachTweet in tweets.data:
        tweetID = eachTweet.id
        userText = eachTweet.text
        break
    
    # isin() methods return Boolean Dataframe of given Dimension
    # the first any() will return boolean series
    # and 2nd any() will return single bool value
    
    df = pd.read_csv(dbPath)
    result = df.isin([tweetID]).any().any()
    if result:
        send("No New Tweets", chat_id=telegramChatID, token=telegramToken)
    else:
        #send(f"Twitter Account: {str(usertwitterAccount.screen_name)} \nTweet ID: {str(tweetID)} \n{userText}", chat_id=telegramChatID, token=telegramToken)
        with open(dbPath, "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([usertwitterAccount.id, tweetID, userText])
        # passing who sent the tweet and the tweet itself after a new tweet is written to the file -> assumption: this will be the latest tweet
        ta.analyseTweet(usertwitterAccount.screen_name, userText)