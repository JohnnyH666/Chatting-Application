import pytest
import requests
import json
from src import config
from datetime import datetime, timezone
from tests.helper import standup_active_v1, standup_send_v1, auth_register_v2, channel_join_v2, channels_create_v2, auth_login_v2, auth_logout_v1, standup_start_v1
from src.data_store import data_store
import time
@pytest.fixture
def setup():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register_a_user1():
    return auth_register_v2('Libo@gmail.com', '1234567', 'Libo', 'Cheng')

@pytest.fixture
def register_a_user2():
    return auth_register_v2('Linlin@gmail.com', '1234567', 'Linlin', 'Luo')

#-------------------standup_start_v1_test--------------------------
def test_standup_start_invalid_token_1(setup):
    assert standup_start_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                            'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 1, 1)['code'] == 403

def test_standup_start_invalid_token_2(setup, register_a_user1):
    resp_login = auth_login_v2('Libo@gmail.com', '1234567')
    auth_logout_v1(resp_login['token'])
    assert standup_start_v1(resp_login['token'], 1, 1)['code'] == 403

def test_standup_start_user_not_in_channel(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    user2 = register_a_user2
    resp_login = auth_login_v2('Libo@gmail.com', '1234567')
    channel1 = channels_create_v2(user1['token'], 'love', True)
    auth_logout_v1(resp_login['token'])
    auth_login_v2('Linlin@gmail.com', '1234567')
    assert standup_start_v1(user2['token'], channel1['channel_id'], 1)['code'] == 403

def test_standup_start_invalid_channel(setup, register_a_user1):
    user1 = register_a_user1
    auth_login_v2('Libo@gmail.com', '1234567')
    assert standup_start_v1(user1['token'], 1, 1)['code'] == 400

def test_standup_start_negative_length(setup, register_a_user1):
    user1 = register_a_user1
    channel1 = channels_create_v2(user1['token'], 'love', True)
    auth_login_v2('Libo@gmail.com', '1234567')
    assert standup_start_v1(user1['token'], channel1['channel_id'], -1)['code'] == 400

def test_standup_start_is_active(setup, register_a_user1):
    user1 = register_a_user1
    auth_login_v2('Libo@gmail.com', '1234567') 
    channel1 = channels_create_v2(user1['token'], 'love', True)
    standup_start_v1(user1['token'], channel1['channel_id'], 10)
    assert standup_start_v1(user1['token'], channel1['channel_id'], 5)['code'] == 400

def test_standup_start_success(setup, register_a_user1):
    user1 = register_a_user1 
    channel1 = channels_create_v2(user1['token'], 'love', True)
    t = standup_start_v1(user1['token'], channel1['channel_id'], 1)
    standup_send_v1(user1['token'], channel1['channel_id'], 'happy')
    time.sleep(2)
    assert t == {'time_finish': int(datetime.now(timezone.utc).timestamp() - 1)}

#-------------------standup_active_v1_test--------------------------
# Test if AccessError occurs when token and channel_id are invalid
def test_standup_active_invalid_token(setup):
    assert standup_active_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                            'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 1)['code'] == 403

# Test if AccessError occurs when token is invalid due to logout
def test_standup_active_invalid_token_2(setup, register_a_user1):
    user1 = register_a_user1 
    channel1 = channels_create_v2(user1['token'], 'love', True)
    resp_login = auth_login_v2('Libo@gmail.com', '1234567')
    auth_logout_v1(resp_login['token'])
    
    assert standup_active_v1(resp_login['token'], channel1['channel_id'])['code'] == 403
    

# Test if InputError occurs when channel_id is invalid and token is valid 
def test_standup_active_valid_token_and_invalid_channel_id(setup, register_a_user1):
    user1 = register_a_user1
    assert standup_active_v1(user1['token'], 1234)['code'] == 400

# Test if AccessError occurs when the authorised user is not the member of channel 
def test_standup_active_invalid_user(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1 
    channel1 = channels_create_v2(user1['token'], 'love', True)
    user2 = register_a_user2
    assert standup_active_v1(user2['token'], channel1['channel_id'])['code'] == 403

# Test whether a standup is a active
def test_standup_active_is_not_active(setup, register_a_user1):
    user1 = register_a_user1 
    channel1 = channels_create_v2(user1['token'], 'love', True)
    assert standup_active_v1(user1['token'], channel1['channel_id']) == {'is_active': False, 'time_finish': None}

def test_standup_active_is_active(setup, register_a_user1):
    user1 = register_a_user1 
    channel1 = channels_create_v2(user1['token'], 'love', True)
    resp = standup_start_v1(user1['token'], channel1['channel_id'], 10)
    assert standup_active_v1(user1['token'], channel1['channel_id']) == {'is_active': True, 'time_finish': resp['time_finish']}


#-------------------standup_send_v1_test--------------------------
# Test if AccessError occurs when token and channel_id are invalid
def test_standup_send_invalid_token(setup):
    assert standup_send_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                            'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 1, 'happy')['code'] == 403

# Test if AccessError occurs when token is invalid due to logout
def test_standup_send_invalid_token_2(setup, register_a_user1):
    user1 = register_a_user1 
    channel1 = channels_create_v2(user1['token'], 'love', True)
    standup_start_v1(user1['token'], channel1['channel_id'], 10)
    resp_login = auth_login_v2('Libo@gmail.com', '1234567')
    auth_logout_v1(resp_login['token'])
    
    assert standup_send_v1(resp_login['token'], channel1['channel_id'], 'happy')['code'] == 403
    

# Test if InputError occurs when channel_id is invalid and token is valid 
def test_standup_send_valid_token_and_invalid_channel_id(setup, register_a_user1):
    user1 = register_a_user1
    channel1 = channels_create_v2(user1['token'], 'love', True)
    standup_start_v1(user1['token'], channel1['channel_id'], 10)
    assert standup_send_v1(user1['token'], 1234, 'happy')['code'] == 400

# Test if InputError occurs when length of message is over 1000 characters
def test_standup_send_length_over_1000(setup, register_a_user1): 
    user1 = register_a_user1 
    channel1 = channels_create_v2(user1['token'], 'love', True)
    standup_start_v1(user1['token'], channel1['channel_id'], 10)  
    message = 'Linlin'*1000
    assert standup_send_v1(user1['token'], channel1['channel_id'], message)['code'] == 400

# Test if InputError occurs when an active standup is not currently running in the channel
def test_standup_send_is_not_active_now(setup, register_a_user1): 
    user1 = register_a_user1 
    channel1 = channels_create_v2(user1['token'], 'love', True)  
    assert standup_send_v1(user1['token'], channel1['channel_id'], 'happy')['code'] == 400

# Test if AccessError occurs when the authorised user is not the member of channel 
def test_standup_send_invalid_user(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1 
    channel1 = channels_create_v2(user1['token'], 'love', True)
    standup_start_v1(user1['token'], channel1['channel_id'], 10)
    user2 = register_a_user2
    assert standup_send_v1(user2['token'], channel1['channel_id'], 'happy')['code'] == 403

# Test send message successful
def test_standup_send_message_sucessful(setup, register_a_user1):
    user1 = register_a_user1 
    channel1 = channels_create_v2(user1['token'], 'love', True)
    standup_start_v1(user1['token'], channel1['channel_id'], 10)
    assert standup_send_v1(user1['token'], channel1['channel_id'], 'happy') == {}


