import pytest
import requests
import json
from src import config
from tests.helper import auth_login_v2, auth_logout_v1, auth_register_v2, channels_create_v2, channel_invite_v2, channel_join_v2, dm_create_v1, message_edit_v1,message_send_v1, message_share_v1, message_react_v1, message_remove_v1, message_senddm_v1, notifications_get_v1, user_profile_uploadphoto_v1, user_stats_v1, users_stats_v1
from tests.helper import setup, register_a_user, register_a_user1

#-------------------notifications_get_v1----------------------
def test_notifications_get_v1_invalid_token(setup):
    resp = notifications_get_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU')
    assert(resp['code'] == 403)

def test_notifications_get_v1_session(setup, register_a_user):
    resp_login = auth_login_v2('erika@gmail.com', '1234567')
    auth_logout_v1(resp_login['token'])
    resp = notifications_get_v1(resp_login['token'])
    assert(resp['code'] == 403)

def test_notifications_get_v1_channel_successful(setup, register_a_user, register_a_user1):
    user = register_a_user
    user1 = register_a_user1
    channel = channels_create_v2(json.loads(user.text)['token'], 'administration', True)
    channel_invite_v2(json.loads(user.text)['token'], channel['channel_id'], json.loads(user1.text)['auth_user_id'])
    resp = notifications_get_v1(json.loads(user.text)['token'])
    assert resp['notifications'] == [{'channel_id': 1, 'dm_id': -1, 'notification_message': 'erikafu added you to administration'}]

def test_notifications_get_v1_dm_and_tag(setup, register_a_user, register_a_user1):
    user = register_a_user
    dm = dm_create_v1(json.loads(user.text)['token'], [2])
    message_senddm_v1(json.loads(user.text)['token'], dm['dm_id'], 'have a good day@yiningzhang')
    resp = notifications_get_v1(json.loads(user.text)['token'])
    assert resp['notifications'] == [{'channel_id': -1, 'dm_id': 1, 'notification_message': 'erikafu tagged you in erikafu, yiningzhang: have a good day@yini'}, 
                                     {'channel_id': -1, 'dm_id': 1, 'notification_message': 'erikafu added you to erikafu, yiningzhang'}]

def test_notifications_get_v1_react_successful(setup, register_a_user):
    user = register_a_user
    channel = channels_create_v2(json.loads(user.text)['token'], 'administration', True)
    message = message_send_v1(json.loads(user.text)['token'], channel['channel_id'],'have a good day')
    message_react_v1(json.loads(user.text)['token'], message['message_id'], 1)
    resp = notifications_get_v1(json.loads(user.text)['token'])
    assert resp['notifications'] == [{'channel_id': 1, 'dm_id': -1, 'notification_message': 'erikafu reacted to your message in administration'}]

def test_notifications_get_v1_edit_message_channel_tagged(setup, register_a_user, register_a_user1):
    user = register_a_user
    user1 = register_a_user1
    channel = channels_create_v2(json.loads(user.text)['token'], 'administration', True)
    channel_join_v2(json.loads(user1.text)['token'], channel['channel_id'] )
    message_send_v1(json.loads(user.text)['token'], channel['channel_id'],'have a good day')
    message_edit_v1(json.loads(user.text)['token'], 0, 'have a good day@yiningzhang')
    resp = notifications_get_v1(json.loads(user.text)['token'])
    assert resp['notifications'] == [{'channel_id': 1, 'dm_id': -1, 'notification_message': 'erikafu tagged you in administration: have a good day@yini'}]

def test_notifications_get_v1_edit_message_dm_tagged(setup, register_a_user, register_a_user1):
    user = register_a_user
    dm = dm_create_v1(json.loads(user.text)['token'], [2])
    message_senddm_v1(json.loads(user.text)['token'], dm['dm_id'],'have a good day')
    message_edit_v1(json.loads(user.text)['token'], 0, 'have a good day@yiningzhang')
    resp = notifications_get_v1(json.loads(user.text)['token'])
    assert resp['notifications'][0] == {'channel_id': -1, 'dm_id': 1, 'notification_message': 'erikafu tagged you in erikafu, yiningzhang: have a good day@yini'}

def test_notifications_get_v1_share_message_tagged(setup, register_a_user, register_a_user1):
    user = register_a_user
    user1 = register_a_user1
    channel = channels_create_v2(json.loads(user.text)['token'], 'administration', True)
    channel_join_v2(json.loads(user1.text)['token'], channel['channel_id'])
    message_send_v1(json.loads(user.text)['token'], channel['channel_id'], 'have a good day')
    message_share_v1(json.loads(user.text)['token'], 0, 'I tag you@yiningzhang', 1, -1)
    resp = notifications_get_v1(json.loads(user.text)['token'])
    assert resp['notifications'] == [{'channel_id': 1, 'dm_id': -1, 'notification_message': 'erikafu tagged you in administration: have a good dayI tag'}]

#-------------------user_profile_uploadphoto_v1_test----------------------
def test_user_profile_uploadphoto_invalid_token(setup):
    resp = user_profile_uploadphoto_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
                        'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg', 1, 1, 2, 2)
    assert(resp['code'] == 403)

def test_user_profile_uploadphoto_invalid_session(setup, register_a_user):
    resp_login = auth_login_v2('erika@gmail.com', '1234567')
    auth_logout_v1(resp_login['token'])
    resp = user_profile_uploadphoto_v1(resp_login['token'], 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg', 1, 1, 2, 2)
    assert(resp['code'] == 403)

def test_user_profile_uploadphoto_invalid_url(setup, register_a_user):
    user = register_a_user
    resp = user_profile_uploadphoto_v1(json.loads(user.text)['token'], 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jaa.jpg', 1, 1, 2, 2)
    assert(resp['code'] == 400)   

def test_user_profile_uploadphoto_exceed_dimension(setup, register_a_user):
    user = register_a_user
    resp = user_profile_uploadphoto_v1(json.loads(user.text)['token'], 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg', 1, 1, 10000, 50)
    assert(resp['code'] == 400)

def test_user_profile_uploadphoto_invalid_x_y(setup, register_a_user):
    user = register_a_user
    resp = user_profile_uploadphoto_v1(json.loads(user.text)['token'], 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg', 50, 1, 1, 50)
    assert(resp['code'] == 400)

def test_user_profile_uploadphoto_invalid_format(setup, register_a_user):
    user = register_a_user
    resp = user_profile_uploadphoto_v1(json.loads(user.text)['token'], 'http://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png', 1, 1, 2, 2)
    assert(resp['code'] == 400) 

def test_user_profile_uploadphotot_successful(setup, register_a_user, register_a_user1):
    user = register_a_user1
    resp = user_profile_uploadphoto_v1(json.loads(user.text)['token'], 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg', 1, 1, 50, 50)
    resp = requests.post(config.url + 'user/profile/uploadphoto/v1', json={
        'token': json.loads(user.text)['token'], 
        'img_url': 'http://cgi.cse.unsw.edu.au/~jas/home/pics/jas.jpg',
        'x_start': 1,
        'y_start': 1,
        'x_end': 50,
        'y_end': 50})
    assert(resp.status_code == 200)

#-------------------user_stats_v1_test----------------------
def test_user_stats_invalid_token(setup):
    resp = user_stats_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                    'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU')
    assert(resp['code'] == 403)

def test_user_stats_invalid_session(setup, register_a_user):
    resp_login = auth_login_v2('erika@gmail.com', '1234567')
    auth_logout_v1(resp_login['token'])
    resp = user_stats_v1(resp_login['token'])
    assert(resp['code'] == 403)

def test_user_stats_successful_original(setup, register_a_user):
    user = register_a_user
    resp = user_stats_v1(json.loads(user.text)['token'])
    assert resp['user_stats']['channels_joined'][-1]['num_channels_joined'] == 0
    assert resp['user_stats']['dms_joined'][-1]['num_dms_joined'] == 0
    assert resp['user_stats']['messages_sent'][-1]['num_messages_sent']== 0
    assert resp['user_stats']['involvement_rate']== 0
    
def test_user_stats_successful(setup, register_a_user):
    user = register_a_user
    channel = channels_create_v2(json.loads(user.text)['token'], 'administration', True)
    dm_create_v1(json.loads(user.text)['token'], [])
    message_send_v1(json.loads(user.text)['token'], channel['channel_id'], 'have a good day')
    message_send_v1(json.loads(user.text)['token'], channel['channel_id'], 'cool')
    message_send_v1(json.loads(user.text)['token'], channel['channel_id'], 'good')
    message_remove_v1(json.loads(user.text)['token'], 0)
    resp = user_stats_v1(json.loads(user.text)['token'])
    assert resp['user_stats']['channels_joined'][-1]['num_channels_joined'] == 1
    assert resp['user_stats']['dms_joined'][-1]['num_dms_joined'] == 1
    assert resp['user_stats']['messages_sent'][-1]['num_messages_sent'] == 3
    assert resp['user_stats']['involvement_rate'] == 3 / 3

def test_user_stats_involvement_rate_greater_1(setup, register_a_user):
    user = register_a_user
    channel = channels_create_v2(json.loads(user.text)['token'], 'administration', True)
    message_send_v1(json.loads(user.text)['token'], channel['channel_id'], 'have a good day')
    message_send_v1(json.loads(user.text)['token'], channel['channel_id'], 'cool')
    message_remove_v1(json.loads(user.text)['token'], 0)
    resp = user_stats_v1(json.loads(user.text)['token'])
    assert resp['user_stats']['involvement_rate'] == 1
   
#-------------------users_stats_v1_test----------------------
def test_users_stats_invalid_token(setup):
    resp = users_stats_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                    'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU')
    assert(resp['code'] == 403)

def test_users_stats_invalid_session(setup, register_a_user):
    resp_login = auth_login_v2('erika@gmail.com', '1234567')
    auth_logout_v1(resp_login['token'])
    resp = users_stats_v1(resp_login['token'])
    assert(resp['code'] == 403)

def test_users_stats_successful_original(setup, register_a_user):
    user = register_a_user
    resp = users_stats_v1(json.loads(user.text)['token'])
    assert resp['workspace_stats']['channels_exist'][-1]['num_channels_exist'] == 0
    assert resp['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == 0
    assert resp['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 0
    assert resp['workspace_stats']['utilization_rate'] == 0

def test_users_stats_successful(setup, register_a_user):
    user = register_a_user
    channel = channels_create_v2(json.loads(user.text)['token'], 'administration', True)
    dm_create_v1(json.loads(user.text)['token'], [])
    message_send_v1(json.loads(user.text)['token'], channel['channel_id'], 'have a good day')
    resp = users_stats_v1(json.loads(user.text)['token'])
    assert resp['workspace_stats']['channels_exist'][-1]['num_channels_exist'] == 1
    assert resp['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == 1
    assert resp['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 1
    assert resp['workspace_stats']['utilization_rate'] == 1