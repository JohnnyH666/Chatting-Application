from src.data_store import data_store
from src.error import AccessError, InputError
from src.helper_functions import getUserFromToken, getSessionFromToken, search_session, search_dm, search_user, search_user_all

from datetime import datetime 

def dm_create_v1(token, u_ids):
    '''
    Description:
    u_ids contains the user(s) that this DM is directed to, and will not include the creator. The creator is the owner 
    of the DM. name should be automatically generated based on the users that are in this DM. The name should be an 
    alphabetically-sorted, comma-and-space-separated list of user handles, e.g. 'ahandle1, bhandle2, chandle3'.

    Arguments:
        token  - string
        u_ids - List of user ids

    Exceptions:
        Inputerror - Occurs when any u_id in u_ids does not refer to a valid user
        
    Return value:
        Returns {dm_id} - A dictionary contain 'dm_id'    
    '''
    store = data_store.get()
    au_id = getUserFromToken(token)
    # Invalid token, user does not exit 
    if not any(users['u_id'] == au_id for users in store['users']):
        raise AccessError(description='Invalid token')
    session_id = getSessionFromToken(token)
    session = search_session(session_id, au_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    # Raise Inputeror if any u_idn in u_ids is invalid
    for u_idn in u_ids: 
        if not any(users['u_id'] == u_idn for users in store['users']):
            raise InputError(description='Invalid u_id')
    
    name_list = []
    creator = search_user('u_id', au_id)
    name_list.append(creator['handle_str'])
    for user in store['users']:
        if user['u_id'] in u_ids:
            name_list.append(user['handle_str'])
    name_list.sort()
    name_string = ", ".join(name_list)
    dm_id = len(store['dms']) + 1
    
    # find the members
    members_list = []
    members_list.append(search_user('u_id', au_id))
    for u_idm in u_ids:
        members_list.append(search_user('u_id', u_idm))
    store['dms'].append({'dm_owner': au_id,
                         'dm_id': dm_id,
                         'name': name_string,
                         'members': members_list,
                         'messages':[]
                        }) 
    # update notifications
    store['notifications'].append({'channel_id': -1, 'dm_id': dm_id, 'notification_message': f"{creator['handle_str']} added you to {name_string}"})
    # update user_stats
    new_user = search_user_all(au_id)
    new_user['dms_joined'].append({'num_dms_joined': new_user['dms_joined'][-1]['num_dms_joined'] + 1, 'time_stamp': int(datetime.timestamp(datetime.now()))})  
    # update workspace_stats
    store['workspace_stats']['dms_exist'].append({'num_dms_exist': len(store['dms']), 'time_stamp': int(datetime.timestamp(datetime.now()))})
    data_store.set(store)
    return {
        'dm_id': dm_id
    }

def dm_list_v1(token):
    '''
    Description:
    Returns the list of DMs that the user is a member of.

    Arguments:
        token  - string

    Exceptions:
        NA

    Return value:
        Returns {dms} - List of dictionaries, where each dictionary contains types { dm_id, name }
    '''
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
    # Invalid token, user does not exit 
    if not any(users['u_id'] == auth_user_id for users in store['users']):
        raise AccessError(description='Invalid token')
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    
    dms_list = []
    target_user = search_user('u_id', auth_user_id)
    for dm in store['dms']:
        for user in dm['members']:
            if user == target_user:
                new_dic = {'dm_id': dm['dm_id'],
                        'name': dm['name'],
                        }   
                dms_list.append(new_dic)
    return {
        'dms': dms_list
    }

def dm_leave_v1(token, dm_id):
    '''
    Given a DM ID, the user is removed as a member of this DM. 
    The creator is allowed to leave and the DM will still exist if this happens. 
    This does not update the name of the DM.

    Arguments:
        token (string) - determine the auth user ID who will leave
        dm_id (Int) - determine which dm the user will leave

    Exceptions:
        AccessError - the token passed in is invalid
        AccessError - dm_id is valid and the authorised user is not a member of the DM
        InputError - dm_id does not refer to a valid DM
        
    Return Value:
        Returns { } when user leave in dm successfully

    '''     

    store = data_store.get()
    u_id = getUserFromToken(token)
    user = search_user('u_id', u_id)
    # invalid token raise AccessError
    if user is None:
        raise AccessError(description='the token passed in is invalid')
    session_id = getSessionFromToken(token)
    session = search_session(session_id, u_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")    
    dm = search_dm('dm_id', dm_id)
    if dm is not None:
        if user not in dm['members']:
            raise AccessError(description="dm_id is valid and the authorised user is not a member of the DM") 
    else:    
        raise InputError(description="dm_id does not refer to a valid DM")      
    dm['members'].remove(user)
    # update user_stats
    new_user = search_user_all(u_id)
    new_user['dms_joined'].append({'num_dms_joined': new_user['dms_joined'][-1]['num_dms_joined'] - 1, 'time_stamp': int(datetime.timestamp(datetime.now()))})  
    data_store.set(store)
    return {
    }                 

def dm_messages_v1(token, dm_id, start): 
    '''
    Given a DM with ID dm_id that the authorised user is a member of, 
    return up to 50 messages between index "start" and "start + 50". 
    Message with index 0 is the most recent message in the DM. This 
    function returns a new index "end" which is the value of "start 
    + 50", or, if this function has returned the least recent messages 
    in the DM, returns -1 in "end" to indicate there are no more messages 
    to load after this return.

    Arguments:
        token (string)    - determine the user ID
        dm_id (integer)   - indicates the dm
        start(integer)    - the index of message that the user want to start return, 
                            which should not be greater than the total message

    Exceptions:
        AccessError - dm_id is valid and the authorised user is not a member of the DM
        AccessError - the token passed in is invalid
        InputError  - dm_id does not refer to a valid DM
        InputError  - start is greater than the total number of messages in the channel

    Return Value:
        Returns 'messages', 'start' and 'end'
    '''
    u_id = getUserFromToken(token)
    user = search_user('u_id', u_id)
    if user is None:
        raise AccessError(description="the token passed in is invalid")

    session_id = getSessionFromToken(token)
    session = search_session(session_id, u_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
        
    dm = search_dm('dm_id', dm_id)
    if dm is not None:
        if user not in dm['members']:
            raise AccessError(description="dm_id is valid and the authorised user is not a member of the DM") 
    else:    
        raise InputError(description="dm_id does not refer to a valid DM")      

    # append all messages into a list called all_messages, 
    # also count the total number of messages
    all_messages = []
    message_size = 0
    for message in dm['messages']:
        all_messages.append(message)
        message_size += 1
    all_messages = list(reversed(all_messages))

    if message_size < int(start):
        raise InputError(description='start is greater than the total number of messages in the channel!')
    
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
    
def message_senddm_v1(token, dm_id, message):
    ''' 
    Send a message from authorised_user to the DM specified by dm_id. 
    Note: Each message should have it's own unique ID, i.e. no messages 
    should share an ID with another message, even if that other message 
    is in a different channel or DM.

    Arguments:
        token (string)                 - determine the user ID 
        dm_id (integer)                - indicates the dm
        message (list of dictionaries) - each dictionary contains types { message_id, u_id, message, time_created }

    Exceptions:
        AccessError - dm_id is valid and the authorised user is not a member of the DM
        AccessError - the token passed in is invalid
        InputError  - dm_id does not refer to a valid DM
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

    dm = search_dm('dm_id', dm_id)
    if dm is not None:
        if user not in dm['members']:
            raise AccessError(description="dm_id is valid and the authorised user is not a member of the DM") 
    else:    
        raise InputError(description="dm_id does not refer to a valid DM")      
    
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
    dm['messages'].append(new_message)
    # update user_stats
    new_user = search_user_all(u_id)
    new_user['messages_sent'].append({'num_messages_sent': new_user['messages_sent'][-1]['num_messages_sent'] + 1, 'time_stamp': int(datetime.timestamp(datetime.now()))})
    #update notification if tag happend
    for member in dm['members']:
        if ('@' + member['handle_str']) in message:
            store['notifications'].append({'channel_id': -1, 'dm_id': dm_id, 'notification_message': f"{user['handle_str']} tagged you in {dm['name']}: {message[:20]}"})
    data_store.set(store)
    return {'message_id': message_id}

def dm_remove_v1(token, dm_id):
    '''
    Description:
    if the authorised user is the original creator of dm of given dm_id , we should remove the dm.

    Arguments:
        store (dictionary)  - data store
        auth_user_id - we can get the auth_user_id of authorised user from the token
        target_dm (dictionary) - the dm of given dm_id
        target_user (dictionary) - authorised user

    Exceptions:
        InputError - Occurs when invalid dm_id
        AccessError - Occurs when invalid token, valid dm_id and the authorised user is not the original dm creator,
                        both token and dm_id are invalid

    Return value:
        Returns {} when the authorised user is the original dm creator
        
    '''
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
    
    # Invaild token
    if not any(user['u_id'] == auth_user_id for user in store['users']):
        raise AccessError(description='Invaild token')

    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description='Invalid token') 
    
    # target dm
    target_dm = search_dm('dm_id', dm_id)
    # Invaild dm_id
    if target_dm is None:
        raise InputError(description='Invaild dm_id')

    # find the target user
    target_user = search_user('u_id', auth_user_id)
    # vaild dm_id and the user is the original DM creator
    if target_dm['dm_owner'] != target_user['u_id']:
        raise AccessError(description='vaild dm_id and the user is the original DM creator')

    # update user_stats
    for user in store['users']: 
        if search_user('u_id', user['u_id']) in target_dm['members']:
            user['dms_joined'].append({'num_dms_joined': user['dms_joined'][-1]['num_dms_joined'] - 1, 'time_stamp': int(datetime.timestamp(datetime.now()))})  
    # update workspace_stats
    store['workspace_stats']['dms_exist'].append({'num_dms_exist': len(store['dms']), 'time_stamp': int(datetime.timestamp(datetime.now()))})
    # remove a dm
    store['dms'].remove(target_dm)
    data_store.set(store)
    return {}

def dm_details_v1(token, dm_id):
    '''
    Description:
    if the authorised user is the member in the dm of given dm_id, we should return the dm deatil

    Arguments:
        store (dictionary)  - data store
        auth_user_id - we can get the auth_user_id of authorised user from the token
        target_dm (dictionary) - the dm of given dm_id
        target_user (dictionary) - authorised user

    Exceptions:
        InputError - Occurs when invalid dm_id
        AccessError - Occurs when invalid token, valid dm_id and the user is not a member of the dm,
                        both token and dm_id are invalid

    Return value:
        Returns {'name', 'members'} when the authorised user is the member in the dm of given valid dm_id
        
    '''
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
 
    # Invalid token
    if not any(user['u_id'] == auth_user_id for user in store['users']):
        raise AccessError(description='Invalid token')

    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description='Invalid token') 

    # target dm
    target_dm = search_dm('dm_id', dm_id)
   
    if target_dm is not None:
        target_user = search_user('u_id', auth_user_id)
        if not any(member == target_user for member in target_dm['members']):
            raise AccessError(description='valid dm_id and the user is not a member of the dm')
    else:
        raise InputError(description='Invalid dm_id')

    return {
        "name": target_dm['name'],
        "members": target_dm['members']
    }