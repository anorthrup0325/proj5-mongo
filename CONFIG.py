"""
Configuration of 'memos' Flask app. 
Edit to fit development or deployment environment.

"""
import random 

### My local development environment
PORT=5000
DEBUG = True
MONGO_URL = "mongodb://editor:simon_pegg@ix.cs.uoregon.edu:4941/memos"  # on Gnat

### On ix.cs.uoregon.edu
#PORT=random.randint(5000,8000)
#DEBUG = False # Because it's unsafe to run outside localhost
#MONGO_URL =  "mongodb://memo:iremember@localhost:4941/memos"  # on ix
