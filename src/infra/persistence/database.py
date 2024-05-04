import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URL'))

db = client.player_stats_db

gamelogs_collection = db['gamelogs']
players_collection = db['players']
scheduled_matchups_collection = db['scheduled_matchups']
projections_collection = db['projections']
teams_collection = db['teams']
test_collection = db['test']