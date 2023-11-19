from flask import Flask
#from pymongo import MongoClient
from .data_fetcher.data_fetcher import DataFetcher
import boto3

app = Flask(__name__)

# MongoDB connection URI (replace with your own URI)
#mongodb_uri = "mongodb://localhost:27017/stockdata"
#app.config["MONGODB_URI"] = mongodb_uri

#DynamoDB connection
dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
db       = dynamodb.Table('stocks')

# Create a MongoDB client and connect using the URI
#client = MongoClient(mongodb_uri)

# Access your MongoDB database
#db = client.get_database()

# Create an instance of the DataFetcher class
data_fetcher = DataFetcher()

# Pass app_name and coin_symbol to all templates
@app.context_processor
def inject_global_variables():
    return dict(app_name="FairPrice", coin_symbol="₿")

# Start the Flask app
if __name__ == "__main__":
    app.run()
