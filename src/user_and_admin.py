from src.data_store import data_store
from src.error import AccessError, InputError
from src.helper_functions import generateSessionId, getUserFromToken,  search_user, getSessionFromToken, search_session, generateToken, search_user_all, in_channel, is_owner, in_dm, in_removed_list
from src.channel import channel_leave_v1
from src.direct_message import dm_leave_v1
from src.message import message_edit_v1

import re
VALIDEMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def users_all_v1(token):
    '''
    Description:
    Returns a list of all users and their associated details.

    Arguments:
        token  - string

    Exceptions:
        NA

    Return Value:
        Returns {'users'} - A dicationary contain a list of user
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
    users_list = []
    for user in store['users']:
        if not in_removed_list(user):
            new_dic = {'u_id': user['u_id'],
                    'email': user['email'], 
                    'name_first': user['name_first'], 
                    'name_last': user['name_last'],
                    'handle_str': user['handle_str'],
                    'profile_img_url': user['profile_img_url']
                    }
            users_list.append(new_dic)
    return {
        'users': users_list
    }

def user_profile_v1(token, u_id): 
    '''
    Description:
    For a valid user, returns information about their user_id, email, first name, last name, and handle

    Arguments:
        token  - string
        u_id -  user id

    Exceptions:
        Inputerror - Occurs when u_id does not refer to a valid user

    Return Value:
        Returns { user } - A dictionary containing u_id, email, name_first, name_last, handle_str
    '''
    auth_user_id = getUserFromToken(token)
    auth_user = search_user('u_id', auth_user_id)
    # Invalid token, user does not exit 
    if auth_user is None:
        raise AccessError(description="the token passed in is invalid")
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    
    user = search_user_all(u_id)
    if user is None:   
        raise InputError(description='Invalid u_id')
        
    return { 
        'user': {
            'u_id': user['u_id'],
            'email': user['email'],
            'handle_str': user['handle_str'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'profile_img_url': user['profile_img_url'],
        }
    }

def user_profile_setname_v1(token, name_first, name_last):
    '''
    Update the authorised user's first and last name

    Arguments:
        store (dictionary)  - data store
        auth_user_id - we can get the auth_user_id of authorised user from the token
        target_user (dictionary) - authorised user
        name_first (string) - The frist name of the user which must contain alphanumeric (a-z0-9) character
        name_last (string)  - The last name of the user which must contain alphanumeric (a-z0-9) character

    Exceptions:
        AccessError - Occurs when invalid token
        InputError - length of name_first is not between 1 and 50 characters inclusive
        InputError - length of name_last is not between 1 and 50 characters inclusive

    Return Value:
        Returns {} 

    '''
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
# Invalid token
    if not any(user['u_id'] == auth_user_id for user in store['users']):
        raise AccessError(description='Invaild token')

    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description='Invalid token') 

# Invalid name_first
    if len(name_first) not in range(1, 51):
        raise InputError(description="The length of name_first is not between 1 and 50")

# Invalid name_last
    if len(name_last) not in range(1, 51):
        raise InputError(description="The length of name_last is not between 1 and 50")


# Update the authorised user's first and last name
    for user in store['users']:
       if user['u_id'] == int(auth_user_id):
           user['name_first']= name_first
           user['name_last'] = name_last
    
    for channel in store['channels']:
        if in_channel(auth_user_id, channel):
            for member in channel['all_members']:
                if member['u_id'] == int(auth_user_id):
                    member['name_first'] = name_first
                    member['name_last'] = name_last
        if is_owner(auth_user_id, channel):
            for owner in channel['channel_owner']:
                if owner['u_id'] == int(auth_user_id):
                    owner['name_first'] = name_first
                    owner['name_last'] = name_last
   
    for dm in store['dms']:
        if in_dm(auth_user_id, dm):
            for member in dm['members']:
                if member['u_id'] == int(auth_user_id):
                    member['name_first'] = name_first
                    member['name_last'] = name_last
   
    data_store.set(store)
    return {}

def user_profile_setemail_v1(token, email):
    '''
    Update the authorised user's email address
    
    Arguments:
        store (dictionary)  - data store
        auth_user_id - we can get the auth_user_id of authorised user from the token
        target_user (dictionary) - authorised user
        email (string)      - A valid email address

    Exceptions:
        AccessError - Occurs when invalid token
        InputError - email entered is not a valid email 
        InputError - email address is already being used by another user
        

    Return Value:
        Return {}

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

# invalid format of email
    if not (re.fullmatch(VALIDEMAIL, email)):
        raise InputError(description="Invalid format of email")
    
# email address is already being used by another user
    if any(user['email'] == email for user in store['users']):
        raise InputError(description="Email address is already being used")    

# Update the authorised user's email address
    for user in store['users']:
       if user['u_id'] == int(auth_user_id):
           user['email']= email
    
    for channel in store['channels']:
        if in_channel(auth_user_id, channel):
            for member in channel['all_members']:
                if member['u_id'] == int(auth_user_id):
                    member['email'] = email

        if is_owner(auth_user_id, channel):
            for owner in channel['channel_owner']:
                if owner['u_id'] == int(auth_user_id):
                    owner['email'] = email
                    
    for dm in store['dms']:
        if in_dm(auth_user_id, dm):
            for member in dm['members']:
                if member['u_id'] == int(auth_user_id):
                    member['email'] = email
                   
    data_store.set(store)
    return {}

def user_profile_sethandle_v1(token, handle_str):
    '''
    Update the authorised user's handle
    
    Arguments:
        store (dictionary)  - data store
        auth_user_id - we can get the auth_user_id of authorised user from the token
        target_user (dictionary) - authorised user
        handle_str (string)      - A handle

    Exceptions:
        AccessError - Occurs when invalid token
        InputError - length of handle_str is not between 3 and 20 characters inclusive
        InputError - handle_str contains characters that are not alphanumeric
        InputError - the handle is already used by another user
        

    Return Value:
        Return {}

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

# The length of the handle_str is not between 3 and 20
    if len(handle_str) not in range(3, 20):
        raise InputError(description="The length of handle_str is not between 3 and 20")

# handle_str does not contain alphanumeric characters
    if handle_str.isalnum() == False:
        raise InputError(description="The handle_str is invalid")

# handle_str is already being used by another user
    if any(user['handle_str'] == handle_str for user in store['users']):
        raise InputError(description="handle_str is already being used") 

# Update the authorised user's handle
    for user in store['users']:
       if user['u_id'] == int(auth_user_id):
           user['handle_str']= handle_str
    
    for channel in store['channels']:
        if in_channel(auth_user_id, channel):
            for member in channel['all_members']:
                if member['u_id'] == int(auth_user_id):
                    member['handle_str'] = handle_str

        if is_owner(auth_user_id, channel):
            for owner in channel['channel_owner']:
                if owner['u_id'] == int(auth_user_id):
                    owner['handle_str'] = handle_str
         
    for dm in store['dms']:
        if in_dm(auth_user_id, dm):
            for member in dm['members']:
                if member['u_id'] == int(auth_user_id):
                    member['handle_str'] = handle_str

    data_store.set(store)
    return {}

def admin_userpermission_change_v1(token, u_id, permission_id):
    '''
    Description:
    For a valid user, returns information about their user_id, email, first name, last name, and handle

    Arguments:
        token  - string
        u_id -  user id
        permission_id - 

    Exceptions:
        Inputerror - Occurs when u_id does not refer to a valid user
        Inputerror - Occurs when u_id refers to a user who is the only global owner and they are being demoted to a user
        Inputerror - Occurs when permission_id is invalid
        Accesserror - Occurs when the authorised user is not a global owner

    Return Value:
        Returns { user } - A dictionary containing u_id, email, name_first, name_last, handle_str
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
    if auth_user['permission_id'] != 1:
        raise AccessError(description='The authorised user is not a global owner')
    permission_user = search_user_all(u_id)  
    if permission_user is None:
        raise InputError(description='u_id does not refer to a valid user')  
    num_global_owner = 0
    for users in store['users']:
        if users['permission_id'] == 1:
            num_global_owner += 1
    if u_id == 1 and num_global_owner == 1 and permission_id == 2:
        raise InputError(description='u_id refers to a user who is the only global owner and they are being demoted to a user') 
    if permission_id != 1 and permission_id != 2:
        raise InputError(description='permission_id is invalid') 
    
    for member in store['users']:
        if member['u_id'] == u_id:
            member['permission_id'] = int(permission_id)
    data_store.set(store)
    return {}
    
def admin_user_remove_v1(token, u_id):
    '''
    Description:
    Given a user by their u_id, remove them from the Streams. 
    This means they should be removed from all channels/DMs, and will not be included in the list of users returned by users/all. 
    Streams owners can remove other Streams owners (including the original first owner). 
    Once users are removed, the contents of the messages they sent will be replaced by 'Removed user'. 
    Their profile must still be retrievable with user/profile, however name_first should be 'Removed' and name_last should be 'user'. 
    The user's email and handle should be reusable.

    Arguments:
        token (string) - determine if the auth user ID is global owner
        u_id (Int) - determine which user will be removed

    Exceptions:
        AccessError - the token passed in is invalid
        AccessError - the authorised user is not a global owner     
        Inputerror - u_id does not refer to a valid user
        Inputerror - u_id refers to a user who is the only global owner

    Return Value:
        Returns { } when user be removed by global owner successfully
    '''
    store = data_store.get()
    auth_id = getUserFromToken(token)
    auth_user = search_user_all(auth_id)
    if auth_user is None:
        raise AccessError(description="the token passed in is invalid")
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    if auth_user['permission_id'] != 1:
        raise AccessError(description='the authorised user is not a global owner')    
    user = search_user_all(u_id)
    if user is None:
        raise InputError(description="u_id does not refer to a valid user")    
    search_global_owners = store['users']
    len = 0
    for global_owner in search_global_owners:
        if global_owner['permission_id'] == 1:
            len = len + 1     
    if user['permission_id'] == 1 and len == 1:
         raise InputError(description="u_id refers to a user who is the only global owner")
    new_session_id = generateSessionId()         
    user_token = generateToken(u_id, new_session_id)
    removed_user = search_user('u_id', u_id)
    user['session_list'].append(new_session_id)
    for channel in store['channels']:
        if removed_user in channel['all_members']:
            channel_leave_v1(user_token, channel['channel_id'])
    for dm in store['dms']:
        if removed_user in dm['members']:
            dm_leave_v1(user_token, dm['dm_id'])
    for removed_user in store['users']:
        if removed_user['u_id'] == u_id:
            removed_user['name_first'] = 'Removed'
            removed_user['name_last'] = 'user'
            removed_user['email'] = ''
            removed_user['handle_str'] = ''
            store['removed'].append(removed_user)
    for message in store['messages']:
        if message['u_id'] == u_id:
            message_edit_v1(user_token, message['message_id'], 'Removed user')
    data_store.set(store)
    return {
    }             
