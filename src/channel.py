from datetime import datetime
from src.data_store import data_store
from src.error import AccessError, InputError
from src.helper_functions import search_user, search_channel, getUserFromToken, getSessionFromToken, search_session, search_user, search_user_all, is_owner, in_channel

def channel_messages_v2(token, channel_id, start):
    '''
    Given a channel with ID channel_id that the authorised user is a member of, 
    return up to 50 messages between index "start" and "start + 50". Message with 
    index 0 is the most recent message in the channel. This function returns a 
    new index "end" which is the value of "start + 50", or, if this function has 
    returned the least recent messages in the channel, returns -1 in "end" to 
    indicate there are no more messages to load after this return.

    Arguments:
        token (string)         - determine the user ID
        channel_id (integer)   - An existed channel_id and the user is in that channel
        start(integer)         - the index of message that the user want to start return, 
                                 which should not be greater than the total message

    Exceptions:
        AccessError - channel_id is valid and the authorised user is not a member of the channel
        AccessError - the token passed in is invalid
        InputError  - channel_id does not refer to a valid channel
        InputError  - start is greater than the total number of messages in the channel

    Return Value:
        Returns 'messages', 'start' and 'end'
    '''
    u_id = getUserFromToken(token)
    user = search_user('u_id', u_id)
    if user is None:
        raise AccessError("the token passed in is invalid")

    session_id = getSessionFromToken(token)
    session = search_session(session_id, u_id)
    if session is None:
        raise AccessError("the token passed in is invalid")
        
    channel = search_channel("channel_id", channel_id)
    user = search_user('u_id', u_id)
    if channel is not None: 
        if user not in channel['all_members']:
            raise AccessError("channel_id is valid and the authorised user is not a member of the channel")
    else:
        raise InputError("channel_id does not refer to a valid channel")

    # append all messages into a list called all_messages, 
    # also count the total number of messages
    all_messages = []
    message_size = 0
    for message in channel['messages']:
        all_messages.append(message)
        message_size += 1
    all_messages = list(reversed(all_messages))

    if message_size < int(start):
        raise InputError('start is greater than the total number of messages in the channel!')
    
    end = int(start) + 50
    if message_size < end:
        message = list(all_messages)[int(start) : message_size + 1]
        end = -1
    else:
        message = list(all_messages)[int(start) : end + 1]

    return {
        'messages': message,
        'start': int(start),
        'end': end
    }
   
def channel_leave_v1(token, channel_id):
    '''
    Given a channel with ID channel_id that the authorised user is a member of, remove them as a member of the channel. 
    Their messages should remain in the channel. If the only channel owner leaves, the channel will remain.

    Arguments:
        token (string) - determine the auth user ID who will leave
        channel_id (Int) - determine which channel the user will leave

    Exceptions:
        AccessError - the token passed in is invalid
        AccessError - channel_id is valid and the authorised user is not a member of the channel
        InputError - channel_id does not refer to a valid channel
        
    Return Value:
        Returns { } when user leave in channel successfully

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
    if auth_user in channel['channel_owner']:
        channel['channel_owner'].remove(auth_user)
        channel['owner_id'].remove(auth_id)
    channel['all_members'].remove(auth_user) 
    # update user_stats
    new_user = search_user_all(auth_id)
    new_user['channels_joined'].append({'num_channels_joined': new_user['channels_joined'][-1]['num_channels_joined'] - 1, 'time_stamp': int(datetime.timestamp(datetime.now()))}) 
    data_store.set(store)
    return {
    }            

def channel_addowner_v1(token, channel_id, u_id):
    '''
    Make user with user id u_id an owner of the channel.

    Arguments:
        token (string) - determine the auth user ID who added the user as channel owner
        channel_id (Int) - determine which channel the user will be added to be channel owner
        u_id (Int) - determine which user will be the channel owner

    Exceptions:
        AccessError - the token passed in is invalid
        AccessError - channel_id is valid and the authorised user does not have owner permissions in the channel
        InputError - channel_id does not refer to a valid channel
        InputError - u_id is invalid
        InputError - u_id refers to a user who is not a member of the channel
        InputError - u_id refers to a user who is already an owner of the channel

    Return Value:
        Returns { } when user be channel owner successfully

    '''  
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
    auth_user = search_user_all(auth_user_id)
    # invalid token raise AccessError
    if auth_user is None:
        raise AccessError(description='the token passed in is invalid')
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")    
    channel = search_channel('channel_id', channel_id)
    if channel is not None:
        if (not is_owner(auth_user_id, channel)) and (auth_user['permission_id'] != 1):
            raise AccessError("channel_id is valid and the authorised user does not have owner permissions in the channel") 
        elif (auth_user['permission_id'] == 1) and (not in_channel(auth_user_id, channel)):
            raise AccessError("channel_id is valid and the authorised user does not have owner permissions in the channel") 
    else:    
        raise InputError(description="channel_id does not refer to a valid channel")    
    user = search_user('u_id', u_id)
    if user is None:
        raise InputError(description="u_id is invalid")
    if user not in channel['all_members']:
         raise InputError(description="u_id refers to a user who is not a member of the channel")
    if user in channel['channel_owner']:
        raise InputError(description="u_id refers to a user who is already an owner of the channel")    
    channel['channel_owner'].append(user) 
    channel['owner_id'].append(u_id)
    data_store.set(store)
    return {
    }                 

def channel_removeowner_v1(token, channel_id, u_id):
    '''
    Remove user with user id u_id as an owner of the channel.

    Arguments:
        token (string) - determine the auth user ID who remove user
        channel_id (Int) - determine which channel the user will be removed
        u_id (Int) - determine which user will be removed in the channel

    Exceptions:
        AccessError - the token passed in is invalid
        AccessError - channel_id is valid and the authorised user does not have owner permissions in the channel
        InputError - channel_id does not refer to a valid channel
        InputError - u_id is invalid
        InputError - u_id u_id refers to a user who is not an owner of the channel
        InputError - u_id u_id refers to a user who is currently the only owner of the channel

    Return Value:
        Returns { } when user is removed in channel successfully

    '''  
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
    auth_user = search_user_all(auth_user_id)
    # invalid token raise AccessError
    if auth_user is None:
        raise AccessError(description='the token passed in is invalid')
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")    
    channel = search_channel('channel_id', channel_id)
    if channel is not None:
        if auth_user not in channel['channel_owner'] and auth_user['permission_id'] != 1:
            raise AccessError(description="channel_id is valid and the authorised user does not have owner permissions in the channel") 
    else:    
        raise InputError(description="channel_id does not refer to a valid channel")    
    user = search_user('u_id', u_id)
    if user is None:
        raise InputError(description="u_id is invalid")
    if user not in channel['channel_owner']:
        raise InputError(description="u_id refers to a user who is not an owner of the channel")
    if len(channel['channel_owner']) == 1:
        raise InputError(description="u_id refers to a user who is currently the only owner of the channel")    
    channel['channel_owner'].remove(user)
    channel['owner_id'].remove(u_id) 
    data_store.set(store)
    return {
    }             

def channel_join_v2(token, channel_id):
    '''
    Description:
    Given a channel_id of a channel that the authorised user can join, adds them to that channel.

    Arguments:
        token (string) - determine the auth user ID who join the channel
        channel_id (int)    - the channel which ID is 'channel_id'
        
    Exceptions:
        AccessError - the token passed in is invalid
        AccessError - channel_id refers to a channel that is private and the authorised user is not already a channel member and is not a global owner
        InputError  - channel_id does not refer to a valid channel
        InputError  - the authorised user is already a member of the channel

    Return Value:
        Returns <return {}>
    '''
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
    user = search_user('u_id', auth_user_id)
    
    # invalid token raise AccessError
    if user is None:
        raise AccessError(description='the token passed in is invalid')
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid") 
 
    channel = search_channel('channel_id', channel_id)
    if channel is not None: 
        permission_id = search_user_all(auth_user_id)['permission_id'] 
        if (not channel['is_public']) and (permission_id != 1) and (user is not channel['all_members']): 
            raise AccessError(description="channel_id refers to a channel that is private and the authorised user is not already a channel member and is not a global owner")
    else:
        raise InputError(description="channel_id does not refer to a valid channel") 
    if user in channel['all_members']:
        raise InputError(description="the authorised user is already a member of the channel")
    channel['all_members'].append(user)
    # update user_stats
    new_user = search_user_all(auth_user_id)
    new_user['channels_joined'].append({'num_channels_joined': new_user['channels_joined'][-1]['num_channels_joined'] + 1, 'time_stamp': int(datetime.timestamp(datetime.now()))})  
    data_store.set(store)
    return {
    }

def channel_invite_v2(token, channel_id, u_id):
    '''
    Description:
    Invites a user with ID u_id to join a channel with ID channel_id. 
    Once invited, the user is added to the channel immediately. 
    In both public and private channels, all members are able to invite users.

    Arguments:
        channel_id (dictionary)    - the channel which ID is 'channel_id'
        u_id (int) - determine which user will be invited in the channel
        token (string) - determine the auth user ID who invite other user

    Exceptions:
        AccessError - the token passed in is invalid
        AccessError - channel_id is valid and the authorised user is not a member of the channel
        InputError  - channel_id does not refer to a valid channel
        InputError  - u_id does not refer to a valid user
        InputError  - u_id refers to a user who is already a member of the channel

    Return Value:
        Returns {}

    '''
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
    auth_user = search_user('u_id', auth_user_id)
    # invalid token raise AccessError
    if auth_user is None:
        raise AccessError(description='the token passed in is invalid')
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")       
    channel = search_channel('channel_id', channel_id)    
    # Channel_id is valid and the authorised user is not a member of the channel
    if channel is not None: 
        if auth_user not in channel['all_members']:
            raise AccessError(description="channel_id is valid and the authorised user is not a member of the channel")
    else:
        raise InputError(description="channel_id does not refer to a valid channel")    
    user = search_user('u_id', u_id)   
    if user is None:
        raise InputError(description="u_id does not refer to a valid user")
    if user in channel['all_members']:
        raise InputError(description="u_id refers to a user who is already a member of the channel") 
    channel['all_members'].append(user)

    # update notifications
    store['notifications'].append({'channel_id': channel_id, 'dm_id': -1, 'notification_message': f"{auth_user['handle_str']} added you to {channel['name']}"})
    # update user stats
    new_user = search_user_all(auth_user_id)
    new_user['channels_joined'].append({'num_channels_joined': new_user['channels_joined'][-1]['num_channels_joined'] + 1, 'time_stamp': int(datetime.timestamp(datetime.now()))}) 
    data_store.set(store)
    return {
    }    

def channel_details_v2(token, channel_id):
    '''
    Description:
    if the authorised user is the member in the channel of given channel_id, we should return the channel deatil

    Arguments:
        store (dictionary)  - data store
        auth_user_id - we can get the auth_user_id of authorised user from the token
        target_channel (dictionary) - the channel of given channel_id
        target_user (dictionary) - authorised user

    Exceptions:
        InputError - Occurs when invalid channel_id
        AccessError - Occurs when invalid token, valid channel_id and the user is not a member of the channel,
                        both token and channel_id are invalid

    Return value:
        Returns {'name', 'is_public', 'owner_members', 'all_members'} when the authorised user is the member in the channel of given valid channel_id
        
    '''
    auth_user_id = getUserFromToken(token)
 
    target_channel = search_channel('channel_id', channel_id)
   
    target_user = search_user('u_id', auth_user_id)
    # Invalid token
    if target_user is None:
        raise AccessError(description='Invalid token')

    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description='Invalid token')  
   
    # find the target user
    target_user = search_user('u_id', auth_user_id)
    # valid channel_id and the user is not a member of the channel
    if target_channel is not None: 
        if target_user not in target_channel['all_members']:
            raise AccessError(description="channel_id is valid and the authorised user is not a member of the channel")
    else:
        raise InputError(description="channel_id does not refer to a valid channel")    

    return {
        "name": target_channel['name'],
        "is_public": target_channel['is_public'],
        "owner_members": target_channel['channel_owner'],
        "all_members": target_channel["all_members"]
    }