from src.data_store import data_store
from src.error import AccessError, InputError
from src.message import message_send_v1
from src.helper_functions import search_channel, getUserFromToken, getSessionFromToken, search_session, search_user, search_user_all
import threading
from datetime import datetime, timezone 

def standup_start_v1(token, channel_id, length):
    '''
    For a given channel, start the standup period whereby for the next "length" seconds if someone calls "standup/send" with a message, 
    it is buffered during the X second window then at the end of the X second window a message will be added to the message queue in the channel from the user who started the standup. 
    "length" is an integer that denotes the number of seconds that the standup occurs for.

    Arguments:
        token (string)                 - determine the user ID 
        channel_id (int)               - determine the channel
        length (int)                   - determine the number of seconds that the standup occur
       
    Exceptions:
        AccessError - token is invalid
        AccessError - channel_id is valid and the authorised user is not a member of the channel
        InputError  - channel_id does not refer to a valid channel
        InputError  - length is a negative integer
        InputError  - an active standup is currently running in the channel

    Return Value:
        Return 'time_finish' if there is no errors was raised
    '''
    store = data_store.get()  
    auth_id = getUserFromToken(token)
    auth_user = search_user('u_id', auth_id)
    if auth_user is None:
        raise AccessError(description="the token passed in is invalid")
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    channel = search_channel('channel_id', channel_id)
    if channel is not None:
        if auth_user not in channel['all_members']:
            raise AccessError(description="channel_id is valid and the authorised user is not a member of the channel") 
    else:
        raise InputError(description="channel_id does not refer to a valid channel")
    if length < 0:
        raise InputError(description="length is a negative integer")
    dic = standup_active_v1(token, channel_id)
    if dic['is_active'] == True:
        raise InputError(description="an active standup is currently running in the channel")            
    time_finish = int(datetime.now(timezone.utc).timestamp() + length)
    channel['is_active'] = True
    channel['time_finish'] = time_finish
    time = threading.Timer(length, standup_end, [token, channel_id])
    time.start()
    data_store.set(store)
    return {
        'time_finish': time_finish
    }

def standup_end(token, channel_id):
    store = data_store.get()
    u_id = getUserFromToken(token)
    channel = search_channel('channel_id', channel_id)
    message_id = len(store['messages'])
    message = '\n'.join(channel['standup_message'])    
    new_message = {
        'message_id': message_id, 
        'u_id': u_id, 
        'message': message, 
        'time_created': int(datetime.timestamp(datetime.now())),
        'reacts':[{'react_id': 1, 
                   'u_ids':[], 
                   'is_this_user_reacted': False
                 }],
        'is_pinned': False
    }
    store['messages'].append(new_message)
    channel['messages'].append(new_message)
    # update user_stats
    new_user = search_user_all(u_id)
    new_user['messages_sent'].append({'num_messages_sent': new_user['messages_sent'][-1]['num_messages_sent'] + 1, 'time_stamp': int(datetime.timestamp(datetime.now()))})
    # update workspace_stats
    store['workspace_stats']['messages_exist'].append({'num_messages_exist': len(store['messages']), 'time_stamp': int(datetime.timestamp(datetime.now()))})
    channel['is_active'] = False
    channel['time_finish'] = None
    channel['standup_message'] = []
    data_store.set(store)

def standup_active_v1(token, channel_id):
    '''
    Description:
    For a given channel, return whether a standup is active in it, and what time the standup finishes. If no standup is active, then time_finish returns None.

    Arguments:
        auth_user_id - we can get the auth_user_id of authorised user from the token
        target_channel (dictionary) - the channel of given channel_id
        target_user (dictionary) - authorised user
        is_active: whether the standup is active
        time_finish: what time the standup finishes

    Exceptions:
        InputError - Occurs when invalid channel_id
        AccessError - Occurs when invalid token, valid channel_id and the user is not a member of the channel,
                        both token and channel_id are invalid

    Return value:
        Returns {'is_active', 'time_finish'} when the authorised user is the member in the channel of given valid channel_id
        
    '''
    auth_user_id = getUserFromToken(token)
    target_user = search_user('u_id', auth_user_id)
    target_channel = search_channel('channel_id', channel_id)
# Invalid token
    if target_user is None:
        raise AccessError(description="the token is invalid")

    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description="the token is invalid")

# valid channel_id and the user is not a member of the channel
    if target_channel is not None: 
        if target_user not in target_channel['all_members']:
            raise AccessError(description="channel_id is valid and the authorised user is not a member of the channel")
    else:
# invalid channel_id 
        raise InputError(description="channel_id does not refer to a valid channel") 

#return is_active and time_finish
    if target_channel['is_active'] is True:
        return {
            "is_active": True,
            "time_finish": target_channel['time_finish']
        }
    else:
        return {
            "is_active": False,
            "time_finish": None
        }


def standup_send_v1(token, channel_id, message):
    '''
    Description:
    Sending a message to get buffered in the standup queue, assuming a standup is currently active. Note: We do not expect @ tags to be parsed as proper tags when sending to standup/send

    Arguments:
        auth_user_id - we can get the auth_user_id of authorised user from the token and auth_user is the message sender
        target_channel (dictionary) - the channel of given channel_id
        target_user (dictionary) - authorised user
        message: message from sender
        new_message: delete @ at message and create a new message
        finish_message: finish message is composed by new_message, ':', and the handle_str of sender

    Exceptions:
        InputError - Occurs when invalid channel_id, length of message is over 1000 characters, an active standup is not currently running in the channel
        AccessError - Occurs when invalid token, valid channel_id and the user is not a member of the channel,
                        both token and channel_id are invalid

    Return value:
        Returns {}
        
    '''
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
    target_user = search_user('u_id', auth_user_id)
    target_channel = search_channel('channel_id', channel_id)
# Invalid token
    if target_user is None:
        raise AccessError(description="the token is invalid")

    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description="the token is invalid")
# valid channel_id and the user is not a member of the channel
    if target_channel is not None: 
        if target_user not in target_channel['all_members']:
            raise AccessError(description="channel_id is valid and the authorised user is not a member of the channel")
    else:
# invalid channel_id 
        raise InputError(description="channel_id does not refer to a valid channel") 
# length of message is over 1000 characters
    if len(message) > 1000:
        raise InputError(description="length of message is over 1000 characters")
# an active standup is not currently running in the channel
    if target_channel['is_active'] is False:
        raise InputError(description="an active standup is not currently running in the channel")

# Sending a message to get buffered in the standup queue
    new_message = message.replace('@', '')
    finish_message = target_user['handle_str'] + ':' + '' + new_message
    target_channel['standup_message'].append(finish_message)
    data_store.set(store)
    return {
    }    

