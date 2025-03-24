# Imports
import re 
import tokenFetcher as tf
from unshortenit import UnshortenIt

# this code is under the assumption that there won't be multiple blockexplorers within the same tweet 
def analyseTweet(tweet: str):
    # Link extraction
    unshortener = UnshortenIt()
    # list of possible blockexplorers that we can connect to
    blockexplorers = ['polygonscan.com/tx/', 'etherscan.io/tx/', 'snowtrace.io/tx/', 'bscscan.com/tx/']
    # regex to search for the twitter shortened links in tweets
    tweetRegex = re.compile(r"[a-zA-Z]+://t\.co/[A-Za-z0-9]+", re.IGNORECASE)
    link = [unshortener.unshorten(uri=eachWord.group()) for eachWord in tweetRegex.finditer(tweet) for eachLink in blockexplorers if re.search(eachLink, unshortener.unshorten(uri=eachWord.group()))]
    # finds the hash from the link
    txHash = re.findall(r"/tx/([A-Za-z0-9]+)", link[0])[0]
    # iterates over all blockexplorers and checks if the link is in there
    whichExplorer = [element for element in blockexplorers if element in link[0]][0]
    # sends TF the transactions hash to know exactly which tx we are querying + sends over the explorer so we can connect to the correct chain
    print(f"\nBlockchain: {whichExplorer} \nTransaction: {txHash}")
    tf.getTokens(txHash, whichExplorer)
