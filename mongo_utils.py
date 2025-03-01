import os
import yaml
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

def get_mongodb_uri():
    """
    Get MongoDB URI from environment variables or app.yaml
    """
    # First try environment variables
    mongodb_uri = os.environ.get('MONGODB_URI')
    
    # If not found, try app.yaml
    if not mongodb_uri:
        try:
            with open('app.yaml', 'r') as yaml_file:
                config = yaml.safe_load(yaml_file)
                env_vars = config.get('env_variables', {})
                mongodb_uri = env_vars.get('MONGODB_URI')
        except Exception:
            pass
    
    # Finally, try .env file (should be loaded by dotenv)
    if not mongodb_uri:
        mongodb_uri = os.getenv('MONGODB_URI')
    
    return mongodb_uri

def get_db_connection():
    """
    Connect to MongoDB and return the database and collection
    """
    mongodb_uri = get_mongodb_uri()
    if not mongodb_uri:
        return None, None
    
    client = MongoClient(mongodb_uri)
    db = client['streamlitchat']
    collection = db['chatrecords']
    return db, collection

def store_chat_message(session_id, user_message, bot_response, platform="unknown", ip_address="unknown", model="gemini-1.5-pro"):
    """
    Store a chat message in MongoDB
    """
    _, collection = get_db_connection()
    if collection is None:  # Correct way to check
        return False
        
    chat_document = {
        'session_id': session_id,
        'timestamp': datetime.utcnow(),
        'user_message': user_message,
        'bot_response': bot_response,
        'platform': platform,
        'ip_address': ip_address,
        'model': model
    }
    
    collection.insert_one(chat_document)
    return True

def get_chat_history_by_session(session_id):
    """
    Get chat history for a specific session
    """
    _, collection = get_db_connection()
    if collection is None:  # Correct way to check
        return []
        
    history = list(collection.find(
        {'session_id': session_id},
        {'_id': 0, 'user_message': 1, 'bot_response': 1, 'timestamp': 1}
    ).sort('timestamp', 1))
    
    return history
