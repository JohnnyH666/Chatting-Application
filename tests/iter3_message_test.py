import pytest
from tests.helper import auth_register_v2, channel_join_v2, channels_create_v2, message_react_v1, message_unreact_v1, clear_v1, auth_login_v2, auth_logout_v1, message_send_v1, message_pin_v1, message_unpin_v1, channel_join_v2, dm_create_v1, message_senddm_v1, message_share_v1, message_sendlater_v1, message_sendlaterdm_v1, search_v1
from datetime import datetime, timezone
import time
@pytest.fixture
def setup():
    clear_v1()
    auth_register_v2("erika@gmail.com", "123456", "erika", "fu")
    return auth_login_v2("erika@gmail.com", "123456")

@pytest.fixture
def send_a_message(setup):
    token = setup['token']
    channel_id = channels_create_v2(token, 'public', True)['channel_id']
    return message_send_v1(token, channel_id, 'have a good day')

# tests for message_react
def test_message_react_invalid_token_1():
    clear_v1()
    assert message_react_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                            'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 1, 1)['code'] == 403

def test_message_react_invalid_token_2(setup):
    token = setup['token']
    auth_logout_v1(token)
    assert message_react_v1(token, 1, 1)['code'] == 403

def test_message_react_invalid_message_id(setup, send_a_message):
    token = setup['token']
    send_a_message['message_id']
    assert message_react_v1(token, 999, 1)['code'] == 400

def test_message_react_invalid_react_id(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    assert message_react_v1(token, message_id, 0)['code'] == 400

def test_message_react_contains_react_id(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    message_react_v1(token, message_id, 1)
    assert message_react_v1(token, message_id, 1)['code'] == 400

def test_message_react_user_not_in_this_channel_or_dm(send_a_message):
    message_id = send_a_message['message_id']
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    assert message_react_v1(token1, message_id, 1)['code'] == 400

def test_message_react_successful_in_channel(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    assert message_react_v1(token, message_id, 1) == {}
    assert message_unreact_v1(token, message_id, 1) == {}
    
def test_message_react_successful_in_dm(setup):
    token = setup['token']
    dm_id = dm_create_v1(token, [])['dm_id']
    message_id = message_senddm_v1(token,dm_id, 'hello')['message_id']
    assert message_react_v1(token, message_id, 1) == {}
    assert message_unreact_v1(token, message_id, 1) == {}
    
# tests for message_unreact
def test_message_unreact_invalid_token_1():
    clear_v1()
    assert message_unreact_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                            'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 1, 1)['code'] == 403

def test_message_unreact_invalid_token_2(setup):
    token = setup['token']
    auth_logout_v1(token)
    assert message_unreact_v1(token, 1, 1)['code'] == 403

def test_message_unreact_invalid_message_id(setup, send_a_message):
    token = setup['token']
    send_a_message['message_id']
    assert message_unreact_v1(token, 999, 1)['code'] == 400

def test_message_unreact_invalid_react_id(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    assert message_unreact_v1(token, message_id, 0)['code'] == 400

def test_message_unreact_contains_unreact_id(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    message_unreact_v1(token, message_id, 1)
    assert message_unreact_v1(token, message_id, 1)['code'] == 400

def test_message_unreact_user_not_in_this_channel_or_dm(send_a_message):
    message_id = send_a_message['message_id']
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    assert message_unreact_v1(token1, message_id, 1)['code'] == 400

def test_message_unreact_does_not_contain_a_react(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    assert message_unreact_v1(token, message_id, 1)['code'] == 400

def test_message_unreact_successful_in_channel(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    message_react_v1(token, message_id, 1)
    assert message_unreact_v1(token, message_id, 1) == {}
    assert message_react_v1(token, message_id, 1) == {}
    
def test_message_unreact_successful_in_dm(setup):
    token = setup['token']
    dm_id = dm_create_v1(token, [])['dm_id']
    message_id = message_senddm_v1(token,dm_id, 'hello')['message_id']
    message_react_v1(token, message_id, 1)
    assert message_unreact_v1(token, message_id, 1) == {}
    assert message_react_v1(token, message_id, 1) == {}

# tests for message_pin
def test_message_pin_invalid_token_1():
    clear_v1()
    assert message_pin_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                            'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 1)['code'] == 403

def test_message_pin_invalid_token_2(setup):
    token = setup['token']
    auth_logout_v1(token)
    assert message_pin_v1(token, 1)['code'] == 403

def test_message_pin_invalid_message(setup, send_a_message):
    token = setup['token']
    send_a_message['message_id']
    assert message_pin_v1(token, 100)['code'] == 400

def test_message_pin_have_no_channel_owner_permission(setup):
    token = setup['token']
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    channel_id = channels_create_v2(token, 'public', True)['channel_id']
    channel_join_v2(token1, channel_id)
    message_id = message_send_v1(token1, channel_id, 'have a good day')['message_id']
    assert message_pin_v1(token1, message_id)['code'] == 403

def test_message_pin_have_no_dm_owner_permission(setup):
    token = setup['token']
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    dm_id = dm_create_v1(token, [2])['dm_id']
    message_id = message_senddm_v1(token1,dm_id, 'hello')['message_id']
    assert message_pin_v1(token1, message_id)['code'] == 403

def test_message_pin_already_pinned(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    message_pin_v1(token, message_id)
    assert message_pin_v1(token, message_id)['code'] == 400

def test_message_pin_user_is_not_in_this_channel(send_a_message):
    clear_v1()
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    auth_register_v2("erika@gmail.com", "123456", "erika", "fu")
    message_id = send_a_message['message_id']
    assert message_pin_v1(token1, message_id)['code'] == 400

def test_message_pin_user_is_not_in_this_dm(setup, send_a_message):
    token = setup['token']
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    dm_id = dm_create_v1(token, [])['dm_id']
    message_id = message_senddm_v1(token,dm_id, 'hello')['message_id']
    assert message_pin_v1(token1, message_id)['code'] == 400

def test_message_pin_successful_in_channel(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    assert message_pin_v1(token, message_id) == {}
    
def test_message_pin_successful_in_dm(setup):
    token = setup['token']
    dm_id = dm_create_v1(token, [])['dm_id']
    message_id = message_senddm_v1(token,dm_id, 'hello')['message_id']
    assert message_pin_v1(token, message_id)== {}


# tests for message_unpin
def test_message_unpin_invalid_token_1():
    clear_v1()
    assert message_unpin_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                            'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 1)['code'] == 403

def test_message_unpin_invalid_token_2(setup):
    token = setup['token']
    auth_logout_v1(token)
    assert message_unpin_v1(token, 1)['code'] == 403

def test_message_unpin_invalid_message(setup, send_a_message):
    token = setup['token']
    send_a_message['message_id']
    assert message_unpin_v1(token, 1)['code'] == 400

def test_message_unpin_have_no_channel_owner_permission(setup):
    token = setup['token']
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    channel_id = channels_create_v2(token, 'public', True)['channel_id']
    channel_join_v2(token1, channel_id)
    message_id = message_send_v1(token1, channel_id, 'have a good day')['message_id']
    assert message_unpin_v1(token1, message_id)['code'] == 403

def test_message_unpin_have_no_dm_owner_permission(setup):
    token = setup['token']
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    dm_id = dm_create_v1(token, [2])['dm_id']
    message_id = message_senddm_v1(token1,dm_id, 'hello')['message_id']
    assert message_unpin_v1(token1, message_id)['code'] == 403

def test_message_unpin_not_already_pinned(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    assert message_unpin_v1(token, message_id)['code'] == 400

def test_message_unpin_user_is_not_in_this_channel(send_a_message):
    clear_v1()
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    auth_register_v2("erika@gmail.com", "123456", "erika", "fu")
    token = auth_login_v2("erika@gmail.com", "123456")['token']
    channel_id = channels_create_v2(token, 'public', True)['channel_id']
    message_id = message_send_v1(token, channel_id, 'have a good day')['message_id']
    message_pin_v1(token, message_id)
    assert message_unpin_v1(token1, message_id)['code'] == 400

def test_message_unpin_user_is_not_in_this_dm(setup, send_a_message):
    token = setup['token']
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    dm_id = dm_create_v1(token, [])['dm_id']
    message_id = message_senddm_v1(token, dm_id, 'hello')['message_id']
    assert message_pin_v1(token1, message_id)['code'] == 400

def test_message_unpin_successful_in_channel(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    message_pin_v1(token, message_id)
    assert message_unpin_v1(token, message_id) == {}
    
def test_message_unpin_successful_in_dm(setup):
    token = setup['token']
    dm_id = dm_create_v1(token, [])['dm_id']
    message_id = message_senddm_v1(token,dm_id, 'hello')['message_id']
    message_pin_v1(token, message_id)
    assert message_unpin_v1(token, message_id) == {}

# tests for message_share
def test_message_share_invalid_token_1():
    clear_v1()
    assert message_share_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                            'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 1, 'have a good day', 1, 1)['code'] == 403

def test_message_share_invalid_token_2(setup):
    token = setup['token']
    auth_logout_v1(token)
    assert message_share_v1(token, 1, 'have a good day', 1, 1)['code'] == 403

def test_user_not_in_this_share_channel_or_dm_1(setup, send_a_message):
    token = setup['token']
    auth_logout_v1(token)
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    message_id = send_a_message['message_id']
    assert message_share_v1(token1, message_id, 'have a good day', 1, -1)['code'] == 403

def test_user_not_in_this_share_channel_or_dm_2(setup):
    token = setup['token']
    dm_id = dm_create_v1(token, [1])['dm_id']
    message_id = message_senddm_v1(token, dm_id, 'hello')['message_id']
    auth_logout_v1(token)
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    assert message_share_v1(token1, message_id, 'have a good day', -1, 1)['code'] == 403

def test_user_share_both_in_channel_and_dm_invalid(setup):
    token = setup['token']
    assert message_share_v1(token, 1, 'have a good day', -1, -1)['code'] == 400

def test_user_share_both_in_channel_and_dm_valid(setup):
    token = setup['token']
    channels_create_v2(token, 'public', True)['channel_id']
    dm_create_v1(token, [1])['dm_id']
    assert message_share_v1(token, 1, 'have a good day', 1, 1)['code'] == 400

def test_og_message_invalid_1(setup):
    token = setup['token']
    channels_create_v2(token, 'public', True)['channel_id']
    assert message_share_v1(token, 1, 'have a good day', 1, -1)['code'] == 400

def test_og_message_invalid_2(setup, send_a_message):  
    token = setup['token']
    auth_logout_v1(token)
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    channels_create_v2(token1, 'public', True)['channel_id']
    message_id = send_a_message['message_id']
    assert message_share_v1(token1, message_id, 'have a good day', 2, -1)['code'] == 400

def test_og_message_invalid_3(setup):
    token = setup['token']
    dm_create_v1(token, [1])['dm_id']
    assert message_share_v1(token, 1, 'have a good day', -1, 1)['code'] == 400

def test_og_message_invalid_4(setup):
    token = setup['token']
    dm_id = dm_create_v1(token, [1])['dm_id']
    message_id = message_senddm_v1(token, dm_id, 'hello')['message_id']
    auth_logout_v1(token)
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    dm_create_v1(token1, [1])
    assert message_share_v1(token1, message_id, 'have a good day', -1, 2)['code'] == 400

def test_user_share_message_is_overlength_1(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    assert message_share_v1(token, message_id, 'have a good day'*10000, 1, -1)['code'] == 400

def test_user_share_message_is_overlength_2(setup):
    token = setup['token']
    dm_id = dm_create_v1(token, [1])['dm_id']
    message_id = message_senddm_v1(token, dm_id, 'hello')['message_id']
    assert message_share_v1(token, message_id, 'have a good day'*10000, -1, 1)['code'] == 400

def test_og_message_success_1(setup, send_a_message):
    token = setup['token']
    message_id = send_a_message['message_id']
    assert message_share_v1(token, message_id, 'have a good day', 1, -1) == {'shared_message_id': 1} 

def test_og_message_success_2(setup):
    token = setup['token']
    dm_id = dm_create_v1(token, [1])['dm_id']
    message_id = message_senddm_v1(token, dm_id, 'hello')['message_id']
    assert message_share_v1(token, message_id, '', -1, dm_id) == {'shared_message_id': 1} 

def test_og_message_success_3(setup, send_a_message):
    token = setup['token']
    dm_create_v1(token, [1])
    message_id = send_a_message['message_id']
    assert message_share_v1(token, message_id, 'have a good day', -1, 1) == {'shared_message_id': 1}       

def test_og_message_success_4(setup):
    token = setup['token']
    dm_id = dm_create_v1(token, [1])['dm_id']
    channels_create_v2(token, 'public', True)['channel_id']
    message_id = message_senddm_v1(token, dm_id, 'hello')['message_id']
    assert message_share_v1(token, message_id, 'have a good day', 1, -1) == {'shared_message_id': 1}       

def test_og_message_success_5(setup, send_a_message):
    token = setup['token']
    channels_create_v2(token, 'public', True)['channel_id']
    message_id = send_a_message['message_id']
    assert message_share_v1(token, message_id, 'have a good day', 2, -1) == {'shared_message_id': 1} 

# tests for message_sendlater
def test_message_sendlater_invalid_token_1():
    clear_v1()
    assert message_sendlater_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                            'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 1, 'have a good day', 1445212800.0)['code'] == 403

def test_message_sendlater_invalid_token_2(setup):
    token = setup['token']
    auth_logout_v1(token)
    assert message_sendlater_v1(token, 1, 'have a good day', 1445212800.0)['code'] == 403

def test_message_sendlater_user_not_in_channel(setup):
    token = setup['token']
    channels_create_v2(token, 'public', True)['channel_id']
    auth_logout_v1(token)
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    assert message_sendlater_v1(token1, 1, 'have a good day', 1445212800.0)['code'] == 403

def test_message_sendlater_invalid_channel(setup):
    token = setup['token']
    assert message_sendlater_v1(token, 1, 'have a good day', 1445212800.0)['code'] == 400

def test_message_sendlater_over_length(setup):
    token = setup['token']
    channels_create_v2(token, 'public', True)['channel_id']
    assert message_sendlater_v1(token, 1, 'have a good day'*1000, 1445212800.0)['code'] == 400    

def test_message_sendlater_past_time_sent(setup):
    token = setup['token']
    channels_create_v2(token, 'public', True)['channel_id']
    assert message_sendlater_v1(token, 1, 'have a good day', 1445212800.0)['code'] == 400    

def test_message_sendlater_success(setup):
    token = setup['token']
    channels_create_v2(token, 'public', True)['channel_id']
    timestamp = int(datetime.now(timezone.utc).timestamp())
    future_time = (timestamp + 1)
    t = message_sendlater_v1(token, 1, 'have a good day', future_time) 
    time.sleep(2)
    assert t == {'message_id': 0}  

# tests for message_sendlaterdm
def test_message_sendlaterdm_invalid_token_1():
    clear_v1()
    assert message_sendlaterdm_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                            'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 1, 'have a good day', 1445212800.0)['code'] == 403

def test_message_sendlaterdm_invalid_token_2(setup):
    token = setup['token']
    auth_logout_v1(token)
    assert message_sendlaterdm_v1(token, 1, 'have a good day', 1445212800.0)['code'] == 403

def test_message_sendlaterdm_user_not_in_channel(setup):
    token = setup['token']
    dm_create_v1(token, [1])['dm_id']
    auth_logout_v1(token)
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    assert message_sendlaterdm_v1(token1, 1, 'have a good day', 1445212800.0)['code'] == 403

def test_message_sendlaterdm_invalid_dm(setup):
    token = setup['token']
    assert message_sendlaterdm_v1(token, 1, 'have a good day', 1445212800.0)['code'] == 400

def test_message_sendlaterdm_over_length(setup):
    token = setup['token']
    dm_create_v1(token, [1])['dm_id']
    assert message_sendlaterdm_v1(token, 1, 'have a good day'*1000, 1445212800.0)['code'] == 400    

def test_message_sendlaterdm_past_time_sent(setup):
    token = setup['token']
    dm_create_v1(token, [1])['dm_id']
    assert message_sendlaterdm_v1(token, 1, 'have a good day', 1445212800.0)['code'] == 400    

def test_message_sendlaterdm_success(setup):
    token = setup['token']
    dm_create_v1(token, [1])['dm_id']
    timestamp = int(datetime.now(timezone.utc).timestamp())
    future_time = (timestamp + 1)
    t= message_sendlaterdm_v1(token, 1, 'have a good day', future_time)
    time.sleep(2)
    assert t == {'message_id': 0}   

# tests for search
def test_search_invalid_token_1():
    clear_v1()
    assert search_v1('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                            'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 'have a good day')['code'] == 403

def test_search_invalid_token_2(setup):
    token = setup['token']
    auth_logout_v1(token)
    assert search_v1(token, 'have a good day')['code'] == 403

def test_search_over_length(setup):
    token = setup['token']
    assert search_v1(token, 'have a good day'*1000)['code'] == 400    

def test_search_lesss_length(setup):
    token = setup['token']
    assert search_v1(token, '')['code'] == 400    

def test_search_channel_success(setup):
    token = setup['token']
    channel_id = channels_create_v2(token, 'public', True)['channel_id']
    message_send_v1(token, channel_id, 'have a good day all')
    assert search_v1(token, 'have a good day')['messages'][0]['message_id'] == 0

def test_search_dm_success(setup):
    token = setup['token']
    dm_id = dm_create_v1(token, [1])['dm_id']
    message_senddm_v1(token, dm_id, 'have a good day all')['message_id']
    assert search_v1(token, 'have a good day')['messages'][0]['message_id'] == 0

def test_search_channel_none():
    clear_v1()
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    channels_create_v2(token1, 'public', True)['channel_id']
    auth_logout_v1(token1)
    token = auth_register_v2("erika@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("erika@gmail.com", "123456")
    channel_id = channels_create_v2(token, 'public', True)['channel_id']
    message_send_v1(token, channel_id, 'cool')
    assert search_v1(token, 'have a good day') == {'messages': []}

def test_search_dm_none():
    clear_v1()
    token1 = auth_register_v2("jie@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("jie@gmail.com", "123456")
    dm_create_v1(token1, [1])['dm_id']
    auth_logout_v1(token1)
    token = auth_register_v2("erika@gmail.com", "123456", "erika", "fu")['token']
    auth_login_v2("erika@gmail.com", "123456")
    dm_id = dm_create_v1(token, [1])['dm_id']
    message_senddm_v1(token, dm_id, 'cool')['message_id']
    assert search_v1(token, 'have a good day') == {'messages': []}
