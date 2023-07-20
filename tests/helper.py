import pytest
import sys
import os
import requests
import json
sys.path.append(os.getcwd())
from src.config import url
from src import config

@pytest.fixture
def setup():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register_a_user():
    return requests.post(config.url + 'auth/register/v2', json={
        'email': 'erika@gmail.com', 
        'password': '1234567', 
        'name_first': 'erika', 
        'name_last': 'fu'})

@pytest.fixture
def register_a_user1():
    return requests.post(config.url + 'auth/register/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567', 
        'name_first': 'Yining', 
        'name_last': 'Zhang'})

def clear_v1():
    requests.delete(url + 'clear/v1')
    
def auth_register_v2(email, password, name_first, name_last):
    return requests.post(url + 'auth/register/v2', json={
            'email': email,
            'password': password,
            'name_first': name_first,
            'name_last': name_last, 
        }).json()

def auth_login_v2(email, password):
    return requests.post(url + 'auth/login/v2', json={
            'email': email,
            'password': password,
        }).json()

def auth_logout_v1(token):
    return requests.post(url + 'auth/logout/v1', json={
            'token': token,
        }).json()

def channels_create_v2(token, name, is_public):
    return requests.post(url + 'channels/create/v2', json={
            'token': token,
            'name': name,
            'is_public': is_public,
        }).json()

def channel_invite_v2(token, channel_id, u_id):
    return requests.post(url + 'channel/invite/v2', json={
            'token': token,
            'channel_id': channel_id,
            'u_id': u_id
        }).json()

def channels_list_v2(token):
    return requests.get(url + 'channels/list/v2', params={
            'token': token,
        }).json()

def message_edit_v1(token, message_id, message):
    return requests.put(url + 'message/edit/v1', json={
            'token': token,
            'message_id': message_id,
            'message': message
        }).json()

def message_remove_v1(token, message_id):
    return requests.delete(url + 'message/remove/v1', json={
            'token': token,
            'message_id': message_id,
        }).json()

def message_react_v1(token, message_id, react_id):
    return requests.post(url + 'message/react/v1', json={
            'token': token,
            'message_id': message_id,
            'react_id': react_id
        }).json()

def message_unreact_v1(token, message_id, react_id):
    return requests.post(url + 'message/unreact/v1', json={
            'token': token,
            'message_id': message_id,
            'react_id': react_id
        }).json()

def message_send_v1(token, channel_id, message):
    return requests.post(url + 'message/send/v1', json={
            'token': token,
            'channel_id': channel_id,
            'message': message
        }).json()

def message_pin_v1(token, message_id):
    return requests.post(url + 'message/pin/v1', json={
            'token': token,
            'message_id': message_id,
        }).json()

def message_unpin_v1(token, message_id):
    return requests.post(url + 'message/unpin/v1', json={
            'token': token,
            'message_id': message_id,
        }).json()


def channel_join_v2(token, channel_id):
    return requests.post(url + 'channel/join/v2', json={
            'token': token,
            'channel_id': channel_id,
        }).json()

def channel_details_v2(token, channel_id):
    return  requests.get(url + 'channel/details/v2', params={
        'token': token,
        'channel_id': channel_id
        }).json()

def dm_create_v1(token, u_ids):
    return requests.post(url + 'dm/create/v1', json={
            'token': token,
            'u_ids': u_ids,
        }).json()

def message_senddm_v1(token, dm_id, message):
    return requests.post(url + 'message/senddm/v1', json={
            'token': token,
            'dm_id': dm_id,
            'message': message
        }).json()


#------------standup--------------------
def standup_start_v1(token, channel_id, length):
    return requests.post(url + 'standup/start/v1', json={
            'token': token,
            'channel_id': channel_id,
            'length': length
        }).json()

def standup_active_v1(token, channel_id):
    return requests.get(url + 'standup/active/v1', params={
            'token': token,
            'channel_id': channel_id,
        }).json()

def standup_send_v1(token, channel_id, message):
    return requests.post(url + 'standup/send/v1', json={
            'token': token,
            'channel_id': channel_id,
            'message': message
        }).json()


#------------message--------------------
def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    return requests.post(url + 'message/share/v1', json={
            'token': token,
            'og_message_id': og_message_id,
            'message': message,
            'channel_id': channel_id,
            'dm_id': dm_id,
        }).json()        

def message_sendlater_v1(token, channel_id, message, time_sent):
    return requests.post(url + 'message/sendlater/v1', json={
            'token': token,
            'channel_id': channel_id,
            'message': message,
            'time_sent': time_sent,
        }).json()        

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    return requests.post(url + 'message/sendlaterdm/v1', json={
            'token': token,
            'dm_id': dm_id,
            'message': message,
            'time_sent': time_sent,
        }).json()   

def search_v1(token, query_str):
    return requests.get(url + 'search/v1', params={
            'token': token,
            'query_str': query_str,
        }).json()  

#------------user_stats_and_users_stats--------------------
def notifications_get_v1(token):
    return requests.get(url + 'notifications/get/v1', params={
            'token': token
        }).json()

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    return requests.post(url + 'user/profile/uploadphoto/v1',json={
            'token': token,
            'img_url': img_url,
            'x_start': x_start,
            'y_start': y_start,
            'x_end': x_end,
            'y_end': y_end
        }).json()

def user_stats_v1(token):
     return requests.get(url + 'user/stats/v1', params={
            'token': token
        }).json()

def users_stats_v1(token):
     return requests.get(url + 'users/stats/v1', params={
            'token': token
        }).json()