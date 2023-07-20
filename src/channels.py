from datetime import datetime
from requests.sessions import session
from src.data_store import data_store
from src.error import AccessError, InputError
from src.helper_functions import search_user, getUserFromToken, getSessionFromToken, search_session, search_user_all

def channels_list_v2(token):
    '''
    Description:
    Provide a list of all channels (and their associated details) that the authorised user is part of..

    Arguments:
        token (string) - a string

    Exceptions:
        AccessError - Occurs when auth_user_id is invalid

    Return Value:
        Returns 'channels': List on successfully
    '''
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
    # Invalid auth_user_id, auth_user_id does not exit.
    if not any(users['u_id'] == auth_user_id for users in store['users']):
        raise AccessError(description='Invalid auth_user_id')
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
        
    List = []
    user = search_user('u_id', auth_user_id)
    for dictionary in store['channels']:
        for member in dictionary['all_members']:
            if user == member:
                new_dic = {'channel_id': dictionary['channel_id'], 
                        'name': dictionary['name']
                        }
                List.append(new_dic)
    return {
        'channels': List
    }

def channels_listall_v2(token):
    '''
    Description:
    Provide a list of all channels which includes the associated details of private channels and public channels

    Arguments:
        store (dictionary)  -data store
        auth_user_id - we can get the auth_user_id of authorised user from the token
        list (list) - a list of all channels which includes the associated details of private channels and public channels
        new_dic (dictionary) - the associated details of one channel

    Exceptions:
        AccessError - Occurs when Invalid token
        
    Return value:
        Returns {'channels'}
    '''
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
    # Invalid auth_user_id, auth_user_id does not exit.
    if not any(users['u_id'] == auth_user_id for users in store['users']):
        raise AccessError(description='Invalid token')

    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description='Invalid token') 

    list = []
    for dictionary in store['channels']:
        new_dic = {'channel_id': dictionary['channel_id'], 
                   'name': dictionary['name']
                  }
        list.append(new_dic)
        
    return {
        'channels': list
    }  	
 	

def channels_create_v2(token, name, is_public):
    '''
    Description:
    Creates a new channel with the given name that is either a public or private channel. The user who created it automatically joins 
    the channel. For this iteration, the only channel owner is the user who created the channel.

    Arguments:
        token (string)    - string
        name (string)    - name of the channel
        is_public (boolean)    - True if publie, False if private

    Exceptions:
        InputError  - Occurs when length of name is less than 1 or more than 20 characters
        AccessError - Occurs when auth_user_id is invalid

    Return Value:
        Returns 'channel_id': channel_id on successfully
    '''
    store = data_store.get()
    u_id = getUserFromToken(token)
    # Invalid token, user does not exit
    user = search_user_all(u_id)
    if user is None:
        raise AccessError("the token passed in is invalid")

    session_id = getSessionFromToken(token)
    session = search_session(session_id, u_id)
    if session is None:
        raise AccessError("the token passed in is invalid")

    # Invalid channel name  
    if len(name) not in range(1, 21):
        raise InputError(description='Length of name is less than 1 or more than 20 characters')
    
    channel_id = len(store['channels']) + 1
    owner = search_user('u_id', u_id)
    store['channels'].append({'channel_owner': [owner],
                              'owner_id': [u_id],
                              'channel_id': channel_id,
                              'name': name,
                              'all_members': [owner],
                              'is_public': is_public,
                              'messages':[],
                              'is_active': False,
                              'time_finish': None,
                              'standup_message': []
                            })
    # update user_stats
    user['channels_joined'].append({'num_channels_joined': user['channels_joined'][-1]['num_channels_joined'] + 1, 'time_stamp': int(datetime.timestamp(datetime.now()))})              
    # update workspace_stats
    store['workspace_stats']['channels_exist'].append({'num_channels_exist': len(store['channels']), 'time_stamp': int(datetime.timestamp(datetime.now()))})
    data_store.set(store)
    return {
        'channel_id': channel_id,
    }