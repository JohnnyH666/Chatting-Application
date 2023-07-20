import requests
from PIL import Image
import urllib.request
import sys
from src.config import url
from src.data_store import data_store
from src.error import AccessError, InputError
from src.helper_functions import getUserFromToken, getSessionFromToken, search_session, search_user_all

def notifications_get_v1(token):
    '''
    Description:
    Return the user's most recent 20 notifications, ordered from most recent to least recent.
    Arguments:
        token  - string

    Exceptions:
        AccessError - Occurs when the token does not refer to a valid user 
        
    Return value:
        Returns { notifications } - List of dictionaries, where each dictionary contains types { channel_id, dm_id, notification_message } 
        where channel_id is the id of the channel that the event happened in, and is -1 if it is being sent to a DM. dm_id is the DM that 
        the event happened in, and is -1 if it is being sent to a channel. Notification_message is a string of the following format for 
        each trigger action:
      
        tagged: "{User’s handle} tagged you in {channel/DM name}: {first 20 characters of the message}"
        reacted message: "{User’s handle} reacted to your message in {channel/DM name}"
        added to a channel/DM: "{User’s handle} added you to {channel/DM name}"
    '''
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
    # Invalid token, user does not exit 
    if not any(users['u_id'] == auth_user_id for users in store['users']):
        raise AccessError(description='Invalid token')
    # Invalid ssession
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    
    notifications_list = []
    for notification in store['notifications']:
        notifications_list.append(notification)
    notifications_list = list(reversed(notifications_list))
    return {
        'notifications': notifications_list[:20]
    }


def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Description:
    Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end). 
    Position (0,0) is the top left. Please note: the URL needs to be a non-https URL (it should just have "http://" 
    in the URL. We will only test with non-https URLs.

    Arguments:
        token  - string
        img_url - string
        x_start - An integer 
        y_start - An integer 
        x_end - An integer 
        y_end - An integer 

    Exceptions:
        AccessError - Occurs when the token does not refer to a valid user 
        InputError - Occurs when img_url returns an HTTP status other than 200
        InputError - Occurs when any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
        InputError - Occurs when x_end is less than x_start or y_end is less than y_start
        InputError - Occurs when image uploaded is not a JPG

    Return value:
        Returns {}  
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
    resp =  requests.get(img_url)
    if resp.status_code != 200:
       raise InputError(description='img_url returns an HTTP status other than 200')    
    if x_end < x_start or y_end < y_start:
        raise InputError(description="Invalid bounds")
    urllib.request.urlretrieve(img_url, f'src/image_download/{auth_user_id}.jpg')
    imageObject = Image.open(f'src/image_download/{auth_user_id}.jpg')
    if (imageObject.format != 'JPEG') and (imageObject.format != 'JPG'): 
        raise InputError(description='image uploaded is not a JPG')
    width, height = imageObject.size 
    if x_start < 0 or y_start < 0 or x_end > width or y_end > height:
        raise InputError(description='any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL')
    cropped = imageObject.crop((x_start, y_start, x_end, y_end))
    cropped.save(f'src/static/{auth_user_id}.jpg')
    for user in store['users']:
        if user['u_id'] == auth_user_id:
            user.update({'profile_img_url': f'url/static/{auth_user_id}.jpg'})
    return {}

def user_stats_v1(token):
    '''
    Description:
    Fetches the required statistics about this user's use of UNSW Streams.
    Arguments:
        token  - string

    Exceptions:
        AccessError - Occurs when the token does not refer to a valid user 
        
    Return value:
        Returns { user_stats } - A dictionary contain {channels_joined: [{num_channels_joined, time_stamp}], 
        dms_joined: [{num_dms_joined, time_stamp}], messages_sent: [{num_messages_sent, time_stamp}], involvement_rate}  
    '''
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
    # Invalid token, user does not exit 
    if not any(users['u_id'] == auth_user_id for users in store['users']):
        raise AccessError(description='Invalid token')
    # Invalid ssession
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    user = search_user_all(auth_user_id)
    numerator = sum([user['channels_joined'][-1]['num_channels_joined'], user['dms_joined'][-1]['num_dms_joined'], user['messages_sent'][-1]['num_messages_sent']])
    denominator = sum([len(store['channels']), len(store['dms']), len(store['messages'])])
    if denominator == 0:
        user['involvement_rate'] = 0
    else: 
        user['involvement_rate'] = numerator/denominator
    if user['involvement_rate'] > 1:
        user['involvement_rate'] = 1
    return {
        'user_stats': {'channels_joined': user['channels_joined'],
                       'dms_joined': user['dms_joined'],
                       'messages_sent': user['messages_sent'],
                       'involvement_rate':  user['involvement_rate']
                      }
    }

def users_stats_v1(token):
    '''
    Description:
    u_ids contains the user(s) that this DM is directed to, and will not include the creator. The creator is the owner 
    of the DM. name should be automatically generated based on the users that are in this DM. The name should be an 
    alphabetically-sorted, comma-and-space-separated list of user handles, e.g. 'ahandle1, bhandle2, chandle3'.

    Arguments:
        token  - string

    Exceptions:
        AccessError - Occurs when the token does not refer to a valid user 
        
    Return value:
        Returns {workspace_stats} - A dictionary contain {channels_exist: [{num_channels_exist, time_stamp}], 
        dms_exist: [{num_dms_exist, time_stamp}], messages_exist: [{num_messages_exist, time_stamp}], utilization_rate}   
    '''
    store = data_store.get()
    auth_user_id = getUserFromToken(token)
    # Invalid token, user does not exit 
    if not any(users['u_id'] == auth_user_id for users in store['users']):
        raise AccessError(description='Invalid token')
    # Invalid ssession
    session_id = getSessionFromToken(token)
    session = search_session(session_id, auth_user_id)
    if session is None:
        raise AccessError(description="the token passed in is invalid")
    
    num_users_joined = 0
    for user in store['users']:
        if user['channels_joined'][-1]['num_channels_joined'] != 0 or user['dms_joined'][-1]['num_dms_joined'] != 0:
            num_users_joined += 1
    store['workspace_stats']['utilization_rate'] = num_users_joined/len(store['users'])
    return {
        'workspace_stats': store['workspace_stats']
    }
    