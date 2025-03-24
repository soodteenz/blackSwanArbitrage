# import 
import os
import monitorTweets as mt
import tweetAnalysis as ta

# Main
if __name__ == "__main__":
    # Check if the csv file for the tweets exists
    if os.path.exists(mt.dbPath):
        mt.fileDoesExist()
        # removes uncessary whitespace within the file
        #mt.cleanup()
    else:
        # runs a function if the file doesn't exist to create a csv file
        mt.fileDoesNotExist()