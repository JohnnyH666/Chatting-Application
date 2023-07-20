import pytest 
import jwt
import uuid
from src.data_store import data_store
from src.other import clear_v1

SECRET = 'F17A_EAGLEsecret'

# Helper function:
# Search a channel and return a channel with associate information in a dictionary structure
def search_channel(key, value):
    store = data_store.get()
    channels = store['channels']
    for channel in channels:
        if channel[key] == int(value):
            return channel
    return None        

# Search a user and return its associate information but not password in a dictionary structure
def search_user(key, value):
    store = data_store.get()
    users = store['users']
    for user in users:
        if user[key] == int(value):
            new_user = {'email': user['email'],
                        'name_first': user['name_first'],
                        'name_last': user['name_last'],
                        'u_id': user['u_id'],
                        'handle_str': user['handle_str']
                      }
            return new_user
    return None  

def search_user_by_email(key, value):
    store = data_store.get()
    users = store['users']
    for user in users:
        if user[key] == value:
            return user
    return None  

def generateSessionId():   
    return str(uuid.uuid1())

def generateToken(u_id, session_id):
    global SECRET
    return jwt.encode({'u_id': u_id, 'session_id': session_id }, SECRET, algorithm='HS256')

def getUserFromToken(token):
    global SECRET
    return jwt.decode(token, SECRET, algorithms=['HS256'])['u_id']
    
def getSessionFromToken(token):
    global SECRET
    return jwt.decode(token, SECRET, algorithms=['HS256'])['session_id']

def search_message(msg_id):
    store = data_store.get()
    for msg in store['messages']:
        if msg['message_id'] == int(msg_id):
            return msg
    return None 

def search_session(session_id, u_id):
    store = data_store.get()
    index = int(u_id) - 1
    for s_id in store['users'][index]['session_list']:
        if s_id == session_id:
            return s_id
    return None 

# Search a dm and return a dm with associate information in a dictionary structure
def search_dm(key, value):
    store = data_store.get()
    dms = store['dms']
    for dm in dms:
        if dm[key] == int(value):
            return dm
    return None   

def search_user_all(u_id):
    store = data_store.get()
    users = store['users']
    for user in users:
        if user['u_id'] == int(u_id):
            return user
    return None  

def in_channel(u_id, channel):
    for member in channel['all_members']:
        if member['u_id'] == int(u_id):
            return True
    return False

def is_owner(u_id, channel):
    for user in channel['channel_owner']:
        if int(u_id) == user['u_id']:
            return True
    return False

def in_dm(u_id, dm):
    for member in dm['members']: 
        if member['u_id'] == int(u_id):
            return True
    return False

def already_contains_a_react_id(message, u_id):
    for react in message['reacts']:
        for u_id in react['u_ids']:
            if u_id == int(u_id):
                if react['is_this_user_reacted']:
                    return True
    return False
    
def find_message_from_channel_or_dm(message_id):
    store = data_store.get()
    for dm in store['dms']:
        for message in dm['messages']:
            if message['message_id'] == int(message_id):
                return message
                
    for channel in store['channels']:
        for message in channel['messages']:
            if message['message_id'] == int(message_id):
                return message

    return {}

def find_message_return_channel_or_dm_id(message_id):
    store = data_store.get()
    for dm in store['dms']:
        for message in dm['messages']:
            if message['message_id'] == int(message_id):
                return dm['dm_id']
                
    for channel in store['channels']:
        for message in channel['messages']:
            if message['message_id'] == int(message_id):
                return channel['channel_id']
    return {}

def check_message_in_channel_or_dm(message_id):
    store = data_store.get()
    for dm in store['dms']:
        for message in dm['messages']:
            if message['message_id'] == int(message_id):
                return 1
                
    for channel in store['channels']:
        for message in channel['messages']:
            if message['message_id'] == int(message_id):
                return 2

    return 0

def in_dm_or_channel(u_id, num):
    store = data_store.get()
    if num == 1:
        for dm in store['dms']:
            for member in dm['members']: 
                if member['u_id'] == int(u_id):
                    return True
    elif num == 2:
        for channel in store['channels']:
            for member in channel['all_members']: 
                if member['u_id'] == int(u_id):
                    return True
    return False

def is_owner_of_dm_or_channel(u_id, number):
    store = data_store.get()
    if number == 1:
        for dm in store['dms']:
            if dm['dm_owner'] == int(u_id):
                return True
            
    elif number == 2:
        for channel in store['channels']:
            for user in channel['channel_owner']:
                if int(u_id) == user['u_id']:
                    return True
    
    return False

def find_if_user_in_channel_or_dm_where_the_message_resides(user, message_id):
    store = data_store.get()
    for dm in store['dms']:
        for message in dm['messages']:
            if (message['message_id'] == int(message_id)) and (user in dm['members']):
                return True
                
    for channel in store['channels']:
        for message in channel['messages']:
            if (message['message_id'] == int(message_id)) and (user in channel['all_members']):
                return True
    return False

def in_removed_list(user):
    store = data_store.get()
    for member in store['removed']:
        if member['u_id'] == user['u_id']:
            return True
    return False