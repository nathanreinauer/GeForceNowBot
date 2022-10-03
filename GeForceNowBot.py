import praw
import config
import time
import os
from datetime import datetime, timedelta
import traceback
from collections import Counter
from praw.models import Comment
from praw.models import Message
from statistics import mean
import re
import winsound
import random
import enchant
from bs4 import BeautifulSoup
import requests

def beep():
    frequency = 1000
    duration = 500
    winsound.Beep(frequency, duration)

def bot_login():
    print("Logging in...")
    r = praw.Reddit(username = config.username,
                password = config.password,
                client_id = config.client_id,
                client_secret = config.client_secret,
                user_agent = "GeForceNowBot v1")
    print("Logged in!\n")
    return r      

def run_bot(r):
    print("")

def getGamesList():
    gamesList = []
    print("Getting list of GeForce NOW games...")
    url = "https://www.gamewatcher.com/news/nvidia-geforce-now-games-list"
    page = requests.get(url)
    html = str(page.content).split('games list below:')[1]
    soup = BeautifulSoup(html, 'html.parser')
    thing = soup.find_all('li')
    for x in thing:
        game = x.get_text().split(" - ")[0].lower()
        gamesList.append(game)
    return gamesList
    
def checkMessages(r):
    newMessageCount = 0
    for item in r.inbox.unread(limit=50):
        newMessageCount += 1
        if "You've been permanently banned from participating in r/" in item.subject or "You've been temporarily banned from participating in r/" in item.subject:
            bannedSub = item.subject.split('/')[1]
            with open("BannedSubs.txt", "a") as f:
                f.write(bannedSub + "\n")
            print("--- r/{} added to the ban list.".format(bannedSub))
            item.mark_read()
            newMessageCount -= 1
        elif "u/geforcenowbot" in item.body.lower():
            gamesList = getGamesList()
            for game in gamesList:
                if game in item.body.lower()
                print("Game found! {}".format(game))
        elif "good bot" in item.body.lower() and not ">" in item.body:
            try:
                with open ("good_bot.txt", "a") as f:
                    f.write("ID: {}, USER: {}, SUB: r/{}\n".format(str(item.id), str(item.author.name), str(item.subreddit)))
                print("--- I'm a Good Bot! Saved to textfile.")
                item.mark_read()
                newMessageCount -= 1
            except:
                print("--- Error! Message/User may have been deleted.")
                continue
    if newMessageCount > 0:
        print("--- {} new message(s) found!".format(str(newMessageCount)))
        
        
def postReply(comment):
    phrase = comment.body
    if phrase[-1] == ".":
        phrase = phrase[:-1]
    replyText = '*' + phrase + '* \N{Eighth Note}\n\n*What a wonderful phrase!* \N{Eighth Note}\n\n*' + phrase + '* \N{Eighth Note}\n\n*Ain\'t no passin\' craaaze!* \N{Eighth Note}\n\n---\n[[sing it!](https://youtu.be/2LhsQMl5vZQ?t=85)]'
    try:
        comment.reply(replyText)
        print("Reply to '" + phrase + "' successfully posted.\n")
        with open ("PastPhrases.txt", "a") as f:
            f.write(deEmojify(phrase) + '[ID: ' + str(comment.id) + ', SUB: r/' + str(comment.subreddit) + ', TIME: ' + str(time.time()) + ']' + "\n")
    except praw.exceptions.APIException as e:
        if e.error_type == "RATELIMIT":
            rateLimitError(e)
        else:
            print(e)

def rateLimitError(e):
    msg = str(e).lower()
    search = re.search(r'\b(minutes)\b', msg)
    minutes = int(msg[search.start()-2]) + 1
    t = datetime.now() + timedelta(minutes = minutes)
    wakeTime = t.strftime("%H:%M:%S")
    print("Ratelimited for " + str(minutes) + " minutes. Will resume at " + wakeTime + ".")
    time.sleep(minutes*60)

def getPastPhrases():
    if not os.path.isfile("PastPhrases.txt"):
        pastPhrases = []
    else:
        with open("PastPhrases.txt", "r") as f:
            pastPhrases = f.read()
            pastPhrases = pastPhrases.split("\n")
            pastPhrases = filter(None, pastPhrases) #This filters out the blank line at the end of the list from '\n'        
    return list(pastPhrases)

def getBannedSubs():
    if not os.path.isfile("BannedSubs.txt"):
        bannedSubs = []
    else:
        with open("BannedSubs.txt", "r") as f:
            bannedSubs = f.read()
            bannedSubs = bannedSubs.split("\n")
            bannedSubs = filter(None, bannedSubs) #This filters out the blank line at the end of the list from '\n'        
    return list(bannedSubs)

r = bot_login()
pastPhrases = getPastPhrases()
bannedSubs = getBannedSubs()

#while True:
   #run_bot(r)
