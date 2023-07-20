#from _typeshed import IdentityFunction
from src.data_store import data_store
from src.error import AccessError, InputError
from src.helper_functions import is_owner_of_dm_or_channel, search_dm, search_user_all, search_channel, getUserFromToken, getSessionFromToken, search_session, search_message, search_user, already_contains_a_react_id, find_message_from_channel_or_dm, find_message_return_channel_or_dm_id, in_dm_or_channel, check_message_in_channel_or_dm, in_dm, find_if_user_in_channel_or_dm_where_the_message_resides
from src.direct_message import message_senddm_v1
import threading
import time
from datetime import datetime, timezone

def message_send_v1(token, channel_id, message):
    ''' 
    Send a message from the authorised user to the channel specified by channel_id. 
    Note: Each message should have its own unique ID, i.e. no messages should share 
    an ID with another message, even if that other message is in a different channel.

    Arguments:
        token (string)                 - determine the user ID 
        channel_id (integer)           - An existed channel_id and the user is in that channel
        message (sting) - string

    Exceptions:
        AccessError - channel_id is valid and the authorised user is not a member of the channel
        AccessError - the token passed in is invalid
        InputError  - channel_id does not refer to a valid channel
        InputError  - length of message is less than 1 or over 1000 characters

    Return Value:
        Return a unique 'message_id' if there is no errors was raised

    '''
    store = data_store.get()
    u_id = getUserFromToken(token)
    user = search_user('u_id', u_id)
    if user is None:
        raise AccessError(description="the token passed in is invalid")

    session_id = getSessionFromToken(token)
    session = search_session(session_id, u_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")

    channel = search_channel("channel_id", channel_id)

    if channel is not None:
        if user not in channel['all_members']:
            raise AccessError(description='the authorised user is not a member of the channel!')
    else:
        raise InputError(description="channel_id does not refer to a valid channel")
    
    if len(message) not in range(1, 1001):
        raise InputError(description="length of message is less than 1 or over 1000 characters")
    
    message_id = len(store['messages']) 
    
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
    # update notification 
    for member in channel['all_members']:
        if ('@' + member['handle_str']) in message:
            store['notifications'].append({'channel_id': channel_id, 'dm_id': -1, 'notification_message': f"{user['handle_str']} tagged you in {channel['name']}: {message[:20]}"})
    data_store.set(store)
    return {'message_id': message_id}
    

def message_edit_v1(token, message_id, message):
    '''
    Given a message, update its text with new text. If the new message is an 
    empty string, the message is deleted.

    Arguments:
        token (string)                 - determine the user ID 
        message_id (integer)           - an existed message_id
        message (string)               - sttring

    Exceptions:
        AccessError - the token passed in is invalid
        AccessError - message_id refers to a valid message in a joined channel/DM but the 
                      message was not sent by the authorised user 
        AccessError - message_id refers to a valid message in a joined channel/DM but the 
                      authorised user does not have owner permissions in the channel/DM               
        InputError  - length of message is over 1000 characters
        InputError  - message_id does not refer to a valid message within a channel/DM 
                      that the authorised user has joined
    Return Value:
        return { }

    '''
    store = data_store.get()
    u_id = getUserFromToken(token)
    user = search_user_all(u_id)
    if user is None:
        raise AccessError(description="the token passed in is invalid")
    
    session_id = getSessionFromToken(token)
    session = search_session(session_id, u_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")

    target_msg = search_message(message_id) 
    position = check_message_in_channel_or_dm(message_id)
    if target_msg is not None:
        if (target_msg['u_id'] != u_id) and (not is_owner_of_dm_or_channel(u_id, position)): 
            raise AccessError(description="the message was not sent by the authorised user or channal/dm owner")
    else:
        raise InputError(description="message_id does not refer to a valid message within a channel/DM that the authorised user has joined")

    if len(message) > 1000:
        raise InputError(description="length of message is over 1000 characters")

    target_msg['messages'] = message
    channel_or_dm = find_message_from_channel_or_dm(message_id)
    channel_or_dm['message'] = message
    if message == '':
        message_remove_v1(token, message_id)
    # update notification
    id = find_message_return_channel_or_dm_id(message_id)
    if check_message_in_channel_or_dm(message_id) == 1:
        dm = search_dm('dm_id', id)
        for member in dm['members']:
            if ('@' + member['handle_str']) in message:
                store['notifications'].append({'channel_id': -1, 'dm_id': id, 'notification_message': f"{user['handle_str']} tagged you in {dm['name']}: {message[:20]}"})
    else:
        channel = search_channel('channel_id', id)
        for member in channel['all_members']:
            if ('@' + member['handle_str']) in message:
                store['notifications'].append({'channel_id': id, 'dm_id': -1, 'notification_message': f"{user['handle_str']} tagged you in {channel['name']}: {message[:20]}"})
    data_store.set(store)
    return { }

def message_remove_v1(token, message_id):
    '''
    Given a message_id for a message, this message is removed from the channel/DM

    Arguments:
        token (string)                 - determine the user ID 
        message_id (integer)           - an existed message_id

    Exceptions:
        AccessError - the token passed in is invalid
        AccessError - message_id refers to a valid message in a joined channel/DM but the 
                      message was not sent by the authorised user 
        AccessError - message_id refers to a valid message in a joined channel/DM but the 
                      authorised user does not have owner permissions in the channel/DM               
        InputError  - message_id does not refer to a valid message within a channel/DM 
                      that the authorised user has joined
    Return Value:
        return { }

    '''
    store = data_store.get()
    u_id = getUserFromToken(token)
    user = search_user_all(u_id)

    if user is None:
        raise AccessError(description="the token passed in is invalid")

    session_id = getSessionFromToken(token)
    session = search_session(session_id, u_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    
    position = check_message_in_channel_or_dm(message_id)
    target_msg = search_message(message_id)
    if target_msg is not None:
        if (target_msg['u_id'] != u_id) and (not is_owner_of_dm_or_channel(u_id, position)): 
            raise AccessError(description="the message was not sent by the authorised user or owner")
    else:
        raise InputError(description="message_id does not refer to a valid message within a channel/DM that the authorised user has joined")

    for channel in store['channels']:
        for message in channel['messages']:
            if int(message_id) == message['message_id']:
                channel['messages'].remove(message) 
                
    for dm in store['dms']:
        for message in dm['messages']:
            if int(message_id) == message['message_id']:
                dm['messages'].remove(message)
                                 
    store['messages'].remove(target_msg)
    

    # update workspace_stats
    store['workspace_stats']['messages_exist'].append({'num_messages_exist': len(store['messages']), 'time_stamp': time})  
    data_store.set(store)
    return {}

def message_react(token, message_id, react_id):
    '''Given a message within a channel or DM the authorised user 
    is part of, add a "react" to that particular message.
    ("react": List of dictionaries, where each dictionary contains types 
    { react_id, u_ids, is_this_user_reacted } where react_id is the id 
    of a react, and u_ids is a list of user id's of people who've reacted 
    for that react. is_this_user_reacted is whether or not the authorised 
    user has been one of the reacts to this post)
    
    Arguments:
        token (string)                 - determine the user ID 
        message_id (integer)           - an existed message_id
        react_id (integer)

    Exceptions:
        InputError  - message_id is not a valid message within a channel or DM that the authorised user has joined
        InputError  - react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1
        InputError  - the message already contains a react with ID react_id from the authorised user

    Return Value:
        return { }
    '''
    store = data_store.get()
    react_id = int(react_id)
    u_id = getUserFromToken(token)
    user = search_user_all(u_id)
    if user is None:
        raise AccessError(description="the token passed in is invalid")
 
    session_id = getSessionFromToken(token)
    session = search_session(session_id, u_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    
    target_msg = search_message(message_id)
    if target_msg is None:
        raise InputError(description="message_id does not refer to a valid message")
    
    position = check_message_in_channel_or_dm(message_id)
    if not in_dm_or_channel(u_id, position):
        raise InputError(description="the user is not in this channel/dm")
    
    if react_id != 1:
        raise InputError(description="react_id is not a valid React ID")

    if already_contains_a_react_id(target_msg, u_id):
        raise InputError(description="Message already contains a react_id from user")
    
    for react in target_msg['reacts']:
        react['is_this_user_reacted'] = True
        react['u_ids'].append(u_id)
    
    dm_or_channel = find_message_from_channel_or_dm(message_id)
    for react in dm_or_channel['reacts']:
        react['is_this_user_reacted'] = True
        react['u_ids'].append(u_id)

    # update notifications
    id = find_message_return_channel_or_dm_id(message_id)
    if check_message_in_channel_or_dm(message_id) == 1:
        dm = search_dm('dm_id', id)
        store['notifications'].append({'channel_id': -1, 'dm_id': id, 'notification_message': f"{user['handle_str']} reacted to your message in {dm['name']}"})
    else:
        channel = search_channel('channel_id', id)
        store['notifications'].append({'channel_id': id, 'dm_id': -1, 'notification_message': f"{user['handle_str']} reacted to your message in {channel['name']}"})
    data_store.set(store)
    return {}

def message_unreact(token, message_id, react_id):
    '''Given a message within a channel or DM the authorised user 
    is part of, remove a "react" to that particular message.
    
    Arguments:
        token (string)                 - determine the user ID 
        message_id (integer)           - an existed message_id
        react_id (integer)

    Exceptions:
        AccessError - token is invalid
        InputError  - message_id is not a valid message within a channel or DM that the authorised user has joined
        InputError  - react_id is not a valid react ID 
        InputError  - the message does not contain a react with ID react_id from the authorised user

    Return Value:
        return { }
    '''
    react_id = int(react_id)
    u_id = getUserFromToken(token)
    user = search_user_all(u_id)
    if user is None:
        raise AccessError(description="the token passed in is invalid")

    session_id = getSessionFromToken(token)
    session = search_session(session_id, u_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    
    target_msg = search_message(message_id)
    if target_msg is None:
        raise InputError(description="message_id does not refer to a valid message")
    
    position = check_message_in_channel_or_dm(message_id)
    if not in_dm_or_channel(u_id, position):
        raise InputError(description="the user is not in this channel/dm")
    
    if react_id != 1:
        raise InputError(description="react_id is not a valid React ID")
    
    if not already_contains_a_react_id(target_msg, u_id):
        raise InputError(description="the message does not contain a react with ID react_id from the authorised user")
    
    for react in target_msg['reacts']:
        react['is_this_user_reacted'] = False
        react['u_ids'].remove(u_id)
    
    dm_or_channel = find_message_from_channel_or_dm(message_id)
    for react in dm_or_channel['reacts']:
        react['is_this_user_reacted'] = False
        react['u_ids'].remove(u_id)
    
    return {}
    

def message_pin_v1(token, message_id):
    '''Given a message within a channel or DM, mark it as "pinned".

    Arguments:
        token (string)                 - determine the user ID 
        message_id (integer)           - an existed message_id
       
    Exceptions:
        AccessError - token is invalid
        AccessError - message_id refers to a valid message in a joined channel/DM and the authorised user does 
                      not have owner permissions in the channel/DM
        InputError  - message_id is not a valid message within a channel or DM that the authorised user has joined
        InputError  - the message is already pinned
    
    Return Value:
        return { }
    '''
    u_id = getUserFromToken(token)
    user = search_user_all(u_id)
    if user is None:
        raise AccessError(description="the token passed in is invalid")

    session_id = getSessionFromToken(token)
    session = search_session(session_id, u_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    
    target_msg = search_message(message_id)
    if target_msg is None:
        raise InputError(description="message_id does not refer to a valid message")
    
    position = check_message_in_channel_or_dm(message_id)
    if not in_dm_or_channel(u_id, position):
        raise InputError(description="the user is not in this channel/dm")
    
    if (user['permission_id'] != 1) and (not is_owner_of_dm_or_channel(u_id, position)): 
        raise AccessError(description="the authorised user does not have owner permissions in the channel/DM")
    
    
    if target_msg['is_pinned']:
        raise InputError(description="the message is already pinned")

    target_msg['is_pinned'] = True
    dm_or_channel = find_message_from_channel_or_dm(message_id)
    dm_or_channel['is_pinned'] = True

    return {}

def message_unpin_v1(token, message_id):
    '''Given a message within a channel or DM, remove its mark as pinned.

    Arguments:
        token (string)                 - determine the user ID 
        message_id (integer)           - an existed message_id
       
    Exceptions:
        AccessError - token is invalid
        AccessError - message_id refers to a valid message in a joined channel/DM and the authorised user does 
                      not have owner permissions in the channel/DM
        InputError  - message_id is not a valid message within a channel or DM that the authorised user has joined
        InputError  - the message is not already pinned
    
    Return Value:
        return { }
    '''
    u_id = getUserFromToken(token)
    user = search_user_all(u_id)
    if user is None:
        raise AccessError(description="the token passed in is invalid")

    session_id = getSessionFromToken(token)
    session = search_session(session_id, u_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    
    target_msg = search_message(message_id)
    if target_msg is None:
        raise InputError(description="message_id does not refer to a valid message")
    
    position = check_message_in_channel_or_dm(message_id)
    if not in_dm_or_channel(u_id, position):
        raise InputError(description="the user is not in this channel/dm")
    target_msg = search_message(message_id)
    
    if (user['permission_id'] != 1) and (not is_owner_of_dm_or_channel(u_id, position)): 
        raise AccessError(description="the authorised user does not have owner permissions in the channel/DM")
    
    if not target_msg['is_pinned']:
        raise InputError(description="the message is not already pinned")

    target_msg['is_pinned'] = False
    dm_or_channel = find_message_from_channel_or_dm(message_id)
    dm_or_channel['is_pinned'] = True

    return {}

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    og_message_id is the ID of the original message. 
    channel_id is the channel that the message is being shared to, and is -1 if it is being sent to a DM. 
    dm_id is the DM that the message is being shared to, and is -1 if it is being sent to a channel. 
    message is the optional message in addition to the shared message, and will be an empty string '' if no message is given. 
    A new message should be sent to the channel/DM identified by the channel_id/dm_id that contains the contents of both the original message and the optional message. 
    The format does not matter as long as both the original and optional message exist as a substring within the new message.

    Arguments:
        token (string)                 - determine the user ID 
        og_message_id (integer)        - the message that user wants to share
        message (string)               - the optional message that user wants to share 
        channel_id (int)               - channel to which messages will be shared 
        dm_id (int)                    - dm to which messages will be shared                 

    Exceptions:
        AccessError - token is invalid
        AccessError - the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised user has not joined the channel or DM they are trying to share the message to
        InputError  - both channel_id and dm_id are invalid
        InputError  - neither channel_id nor dm_id are -1
        InputError  - og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
        InputError  - length of message is more than 1000 characters

    Return Value:
         Return a unique 'shared_message_id' if there is no errors was raised
    '''
    auth_id = getUserFromToken(token)
    auth_user = search_user('u_id', auth_id)
    if auth_user is None:
        raise AccessError(description="the token passed in is invalid")
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    channel = search_channel('channel_id', channel_id)
    dm = search_dm('dm_id', dm_id)
    if (channel is not None) and (dm is None):
        if auth_user not in channel['all_members']:
            raise AccessError(description="the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised user has not joined the channel or DM they are trying to share the message to") 
    if (channel is None) and (dm is not None):
        if auth_user not in dm['members']:
            raise AccessError(description="the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised user has not joined the channel or DM they are trying to share the message to") 
    if (channel is None) and (dm is None):
        raise InputError(description="both channel_id and dm_id are invalid")
    if (channel is not None) and (dm is not None):
        raise InputError(description="neither channel_id nor dm_id are -1")
    target_msg = search_message(og_message_id)
    if target_msg is None:
        raise InputError(description="message_id does not refer to a valid message")
    if not find_if_user_in_channel_or_dm_where_the_message_resides(auth_user, og_message_id):
        raise InputError(description="og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined")    
    if len(message) >= 1001:
        raise InputError(description="length of message is more than 1000 characters")
    og_message = find_message_from_channel_or_dm(og_message_id)
    if message == '':
        new_message = (og_message['message'])
    else:
        new_message = (og_message['message'] + message)
    if (channel is not None) and (dm is None):
        shared_message = message_send_v1(token, channel_id, new_message)
    else:
        shared_message = message_senddm_v1(token, dm_id, new_message)
    return {
        'shared_message_id': shared_message['message_id']
        }

def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    Send a message from the authorised user to the channel specified by 
    channel_id automatically at a specified time in the future.

    Arguments:
        token (string)                 - determine the user ID 
        channel_id (int)               - channel to which messages will be send later 
        message (string)               - the message that user wants to send later 
        time_sent (int)                - which time messages will be sent    
       
    Exceptions:
        AccessError - token is invalid
        AccessError - channel_id is valid and the authorised user is not a member of the channel they are trying to post to
        InputError  - channel_id does not refer to a valid channel
        InputError  - length of message is over 1000 characters
        InputError  - time_sent is a time in the past

    Return Value:
        Return 'message_id' if there is no errors was raised
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
            raise AccessError(description="channel_id is valid and the authorised user is not a member of the channel they are trying to post to") 
    else:    
        raise InputError(description="channel_id does not refer to a valid channel")    
    if len(message) >= 1001:
        raise InputError(description="length of message is over 1000 characters")
    time_now = datetime.now(timezone.utc).timestamp()
    length = int(time_sent - time_now)
    if (length) < 0:
        raise InputError(description="time_sent is a time in the past")
    message_id = len(store['messages']) 
    timer = threading.Timer(length, message_send_v2, [token, channel_id, message, message_id])
    timer.start()
    return {
        'message_id': message_id
    }

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    Send a message from the authorised user to the DM 
    specified by dm_id automatically at a specified time in the future.

    Arguments:
        token (string)                 - determine the user ID 
        dm_id (int)                    - dm to which messages will be send later 
        message (string)               - the message that user wants to send later 
        time_sent (int)                - which time messages will be sent    
       
    Exceptions:
        AccessError - token is invalid
        AccessError - dm_id is valid and the authorised user is not a member of the DM they are trying to post to
        InputError  - dm_id does not refer to a valid DM
        InputError  - length of message is over 1000 characters
        InputError  - time_sent is a time in the past

    Return Value:
        Return 'message_id' if there is no errors was raised
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
    dm = search_dm('dm_id', dm_id)
    if dm is not None:
        if auth_user not in dm['members']:
            raise AccessError(description="dm_id is valid and the authorised user is not a member of the DM they are trying to post to") 
    else:    
        raise InputError(description="dm_id does not refer to a valid DM")    
    if len(message) >= 1001:
        raise InputError(description="length of message is over 1000 characters")
    time_now = datetime.now(timezone.utc).timestamp()
    length = int(time_sent - time_now)
    if (length) < 0:
        raise InputError(description="time_sent is a time in the past")
    message_id = len(store['messages'])   
    timer = threading.Timer(length, message_senddm_v2, [token, dm_id, message, message_id])
    timer.start()
    return {
        'message_id': message_id
    }

def search_v1(token, query_str):
    '''
    Given a query string, return a collection of messages in all of the channels/DMs 
    that the user has joined that contain the query.

    Arguments:
        token (string)                 - determine the user ID 
        query_str (integer)            - the information the user wants to search for 
       
    Exceptions:
        AccessError - token is invalid
        InputError  - length of query_str is less than 1 or over 1000 characters
    
    Return Value:
        Return messages if there is no errors was raised
    '''
    store = data_store.get()  
    auth_id = getUserFromToken(token)
    user = search_user('u_id', auth_id)
    if user is None:
        raise AccessError(description="the token passed in is invalid")

    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    
    if len(query_str) not in range(1, 1001):
        raise InputError(description="length of query_str is less than 1 or over 1000 characters")
    
    all_messages = []
    for dm in store['dms']:
        if user in dm['members']:
            for message in dm['messages']:
                if query_str in message['message']:
                    all_messages.append(message)
                
    for channel in store['channels']:
        if user in channel['all_members']:
            for message in channel['messages']:
                if query_str in message['message']:
                    all_messages.append(message)

    return {
        'messages':all_messages
    }          

def message_send_v2(token, channel_id, message, message_id):
    store = data_store.get()
    u_id = getUserFromToken(token)
    channel = search_channel("channel_id", channel_id)
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
    data_store.set(store)

def message_senddm_v2(token, dm_id, message, message_id):
    store = data_store.get()
    u_id = getUserFromToken(token)
    dm = search_dm('dm_id', dm_id)
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
    dm['messages'].append(new_message)
    # update user_stats
    new_user = search_user_all(u_id)
    new_user['messages_sent'].append({'num_messages_sent': new_user['messages_sent'][-1]['num_messages_sent'] + 1, 'time_stamp': int(datetime.timestamp(datetime.now()))})
    data_store.set(store)
    
