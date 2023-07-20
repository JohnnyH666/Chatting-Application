import pytest
import requests
import json
from src import config

@pytest.fixture
def setup():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register_a_user_then_login_1():
    requests.post(config.url + 'auth/register/v2',json={
        'email': 'erika@gmail.com', 
        'password': '1234567', 
        'name_first': 'erika', 
        'name_last': 'fu'
    })
    return requests.post(config.url + 'auth/login/v2',json={
        'email': 'erika@gmail.com', 
        'password': '1234567', 
    })

@pytest.fixture
def register_a_user_then_login_2():
    requests.post(config.url + 'auth/register/v2',json={
    'email': 'w17a@gmail.com', 
    'password': '1234567', 
    'name_first': 'erika', 
    'name_last': 'fu'
    })
    return requests.post(config.url + 'auth/login/v2',json={
        'email': 'w17a@gmail.com', 
        'password': '1234567', 
    })

@pytest.fixture
def create_a_channel(register_a_user_then_login_2):
    user = register_a_user_then_login_2
    return requests.post(config.url + 'channels/create/v2',json={
        'token': json.loads(user.text)['token'], 
        'name': 'weekend', 
        'is_public': True
    })

@pytest.fixture
def create_a_dm(register_a_user_then_login_2, register_a_user_then_login_1):
    user2 = register_a_user_then_login_2
    register_a_user_then_login_1
    return requests.post(config.url + 'channels/create/v2',json={
        'token': json.loads(user2.text)['token'], 
        'u_ids': [],
    })

@pytest.fixture
def send_a_message(register_a_user_then_login_2, create_a_channel):
    user = register_a_user_then_login_2
    return requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': 1,
        'message': 'have a good day'
    })


# tests for message_send_v1
def test_message_send_unjoined_user(setup, register_a_user_then_login_1, create_a_channel):
    user = register_a_user_then_login_1
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': 1,
        'message': 'have a good day'
    })
    assert(resp.status_code == 403)

def test_message_send_invalid_user(setup):
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU',
        'channel_id': 1,
        'message': 'have a good day'
    })
    assert(resp.status_code == 403)

def test_message_send_invalid_token(setup, register_a_user_then_login_1, create_a_channel):
    user = register_a_user_then_login_1
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(user.text)['token']
    })
    
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': 1,
        'message': 'have a good day'
    })
    assert(resp.status_code == 403)

def test_message_send_invalid_channel_id(setup, register_a_user_then_login_1): 
    user = register_a_user_then_login_1
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': 1,
        'message': 'have a good day'
    })
   
    assert(resp.status_code == 400)

def test_message_send_invalid_length(setup, register_a_user_then_login_2, create_a_channel):
    setup
    user = register_a_user_then_login_2
    create_a_channel
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': 1,
        'message': 'have a good day'*10000
    })
    assert(resp.status_code == 400)

def test_both_invalid_token_and_channel_id(setup, register_a_user_then_login_2):
    user = register_a_user_then_login_2
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(user.text)['token']
    })

    resp = requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': -1,
        'message': 'have a good day'
    })
    assert(resp.status_code == 403)

def test_message_send_successful(setup, register_a_user_then_login_2, create_a_channel):
    user = register_a_user_then_login_2
    channel = create_a_channel
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'message': 'have a good day'
    })

    assert json.loads(resp.text)['message_id'] == 0

    resp1 = requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'message': 'thanks'
    })
    assert json.loads(resp1.text)['message_id'] == 1
  
    resp2 = requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'message': '  '
    })
    assert json.loads(resp2.text)['message_id'] == 2


# tests for message_edit_v1
def test_message_edit_invalid_user(setup):
    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU',
        'message_id': 1,
        'message': 'have a good day'
    })
    assert(resp.status_code == 403)

def test_message_edit_invalid_token(setup, register_a_user_then_login_2, create_a_channel, send_a_message):
    user = register_a_user_then_login_2
    message = send_a_message
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(user.text)['token']
    })
    
    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id'],
        'message': 'have a good weekend!'
    })
    
    assert(resp.status_code == 403)

def test_message_edit_unjoined_user(setup, send_a_message, register_a_user_then_login_1):
    user = register_a_user_then_login_1
    message = send_a_message
    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id'],
        'message': 'have a good day'
    })
    assert(resp.status_code == 403)
    
def test_message_edit_global_owner_cant_edit_member_message_dm(setup, register_a_user_then_login_1, register_a_user_then_login_2):
    user = register_a_user_then_login_1
    user2 = register_a_user_then_login_2
    dm = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(user2.text)['token'], 
                               'u_ids': [1]})
    message = requests.post(config.url + 'message/senddm/v1',json={
        'token': json.loads(user2.text)['token'],
        'dm_id': json.loads(dm.text)['dm_id'],
        'message': 'weekend'})   
    resp = resp = requests.put(config.url + 'message/edit/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id'],
        'message': 'have a good weekend'* 100000
    })
    assert(resp.status_code == 403)

def test_message_edit_invalid_length(setup, register_a_user_then_login_2, create_a_channel, send_a_message):
    user = register_a_user_then_login_2
    message = send_a_message
    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id'],
        'message': 'have a good weekend'* 100000
    })
    assert(resp.status_code == 400)

def test_cannot_edit_deleted_message(setup, register_a_user_then_login_2, send_a_message):
    user = register_a_user_then_login_2
    message = send_a_message
    requests.put(config.url + 'message/edit/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id'],
        'message': ''
    })
    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id'],
        'message': ''
    })
    assert(resp.status_code == 400)

def test_message_edit_invalid_message_id(setup, register_a_user_then_login_2):
    user = register_a_user_then_login_2
    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': -1,
        'message': 'have a good weekend'
    })

    assert(resp.status_code == 400)
    
def test_empty_edit_deletes_message(setup, register_a_user_then_login_2, send_a_message):
    user = register_a_user_then_login_2
    message = send_a_message
    requests.put(config.url + 'message/edit/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id'],
        'message': ''
    })
    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': json.loads(user.text)['token'],
        'channel_id': 1,
        'start': 0
    })
    assert len(json.loads(resp.text)['messages']) == 0

def test_message_edit_successful(setup, register_a_user_then_login_2, send_a_message):
    user = register_a_user_then_login_2
    message = send_a_message
    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id'],
        'message': 'have a good weekend'
    })
    assert(resp.status_code == 200)
    
def test_message_edit_successful_channel_owner(setup, register_a_user_then_login_1, register_a_user_then_login_2):
    user = register_a_user_then_login_1
    user2 = register_a_user_then_login_2
    channel = requests.post(config.url + 'channels/create/v2',json={
        'token': json.loads(user2.text)['token'], 
        'name': 'weekend', 
        'is_public': True
    })
    resp = requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id']
    })   
    message = requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'message': 'have a good day'
    })
    resp = requests.put(config.url + 'message/edit/v1', json={
        'token': json.loads(user2.text)['token'],
        'message_id': json.loads(message.text)['message_id'],
        'message': 'have a good weekend'
    }) 
    assert(resp.status_code == 200)

def test_message_edit_channel_successful(setup, register_a_user_then_login_2, create_a_channel):
    user = register_a_user_then_login_2
    channel = create_a_channel
    message = requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': 1,
        'message': 'have a good day'
    })
    
    requests.put(config.url + 'message/edit/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id'],
        'message': ''
    })
    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': json.loads(user.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'start': 0
    })
    assert json.loads(resp.text) == dict(start=0, end=-1, messages=[])
    assert(resp.status_code == 200)

def test_message_edit_dm_successful(setup, register_a_user_then_login_2):
    user = register_a_user_then_login_2
    dm = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(user.text)['token'], 
                               'u_ids': []})
    message = requests.post(config.url + 'message/senddm/v1',json={
        'token': json.loads(user.text)['token'],
        'dm_id': json.loads(dm.text)['dm_id'],
        'message': 'weekend'})   
    
    requests.put(config.url + 'message/edit/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id'],
        'message': ''
    })
    resp = requests.get(config.url + 'dm/messages/v1',params={
        'token': json.loads(user.text)['token'], 
        'dm_id': json.loads(dm.text)['dm_id'],
        'start': 0})   
    assert(json.loads(resp.text) == dict(start=0, end=-1, messages=[]))
    assert(resp.status_code == 200)


# tests for message_remove_v1
def test_message_remove_invalid_token(setup, register_a_user_then_login_2, create_a_channel, send_a_message):
    user = register_a_user_then_login_2
    message = send_a_message
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(user.text)['token']
    })
    
    resp = requests.delete(config.url + 'message/remove/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id']
    })
    
    assert(resp.status_code == 403)

def test_message_remove_invalid_user(setup):
    resp = requests.delete(config.url + 'message/remove/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU',
        'message_id': -1
    })
    assert(resp.status_code == 403)

def test_message_remove_unjoined_user(setup, register_a_user_then_login_2, create_a_channel, send_a_message, register_a_user_then_login_1):
    message = send_a_message
    user = register_a_user_then_login_1
    resp = requests.delete(config.url + 'message/remove/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id']
    })
    assert(resp.status_code == 403)
    
def test_message_edit_global_owner_cant_remove_member_message_dm(setup, register_a_user_then_login_1, register_a_user_then_login_2):
    user = register_a_user_then_login_1
    user2 = register_a_user_then_login_2
    dm = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(user2.text)['token'], 
                               'u_ids': [1]})
    message = requests.post(config.url + 'message/senddm/v1',json={
        'token': json.loads(user2.text)['token'],
        'dm_id': json.loads(dm.text)['dm_id'],
        'message': 'weekend'})   
    resp = requests.delete(config.url + 'message/remove/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id']
    })
    assert(resp.status_code == 403)

def test_message_remove_invalid_message_id(setup, register_a_user_then_login_2):
    user = register_a_user_then_login_2
    resp = requests.delete(config.url + 'message/remove/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': -1
    })
    assert(resp.status_code == 400)

def test_cannot_remove_deleted_message(setup, register_a_user_then_login_2, send_a_message):
    user = register_a_user_then_login_2
    message = send_a_message
    requests.delete(config.url + 'message/remove/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id']
    })
    resp = requests.delete(config.url + 'message/remove/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id']
    })
    assert(resp.status_code == 400)
    
def test_message_remove_channel_successful(setup, register_a_user_then_login_2, create_a_channel):
    user = register_a_user_then_login_2
    channel = create_a_channel
    requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': 1,
        'message': 'have a good day'
    })
    message = requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user.text)['token'],
        'channel_id': 1,
        'message': 'cool'
    })
    requests.delete(config.url + 'message/remove/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id']
    })
    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': json.loads(user.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'start': 0
    })
    assert(resp.status_code == 200)
    
def test_message_remove_dm_successful(setup, register_a_user_then_login_2):
    user = register_a_user_then_login_2
    dm = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(user.text)['token'], 
                               'u_ids': []})                    
    requests.post(config.url + 'message/senddm/v1',json={
        'token': json.loads(user.text)['token'],
        'dm_id': json.loads(dm.text)['dm_id'],
        'message': 'weekend'}) 
    message = requests.post(config.url + 'message/senddm/v1',json={
        'token': json.loads(user.text)['token'],
        'dm_id': json.loads(dm.text)['dm_id'],
        'message': 'day'})         
    resp = requests.delete(config.url + 'message/remove/v1', json={
        'token': json.loads(user.text)['token'],
        'message_id': json.loads(message.text)['message_id']
    })
    resp = requests.get(config.url + 'dm/messages/v1',params={
        'token': json.loads(user.text)['token'], 
        'dm_id': json.loads(dm.text)['dm_id'],
        'start': 0})   
    assert(resp.status_code == 200)


# tests for channel_messages_v2
def test_channel_message_invalid_token(setup, register_a_user_then_login_2, create_a_channel, send_a_message):
    user = register_a_user_then_login_2
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(user.text)['token']
    })
    
    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': json.loads(user.text)['token'],
        'channel_id': 1,
        'start': 0
    })
   
    assert(resp.status_code == 403)

def test_channel_message_invalid_token_2(setup):
    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU',
        'channel_id': 1,
        'start': 0
    })
    assert(resp.status_code == 403)

def test_channel_message_not_a_member(setup, register_a_user_then_login_2, create_a_channel, send_a_message, register_a_user_then_login_1):
    user = register_a_user_then_login_1
    channel = create_a_channel
    
    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': json.loads(user.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'start': 0
    })
    
    assert(resp.status_code == 403)

def test_channel_messages_invalid_channel(setup, register_a_user_then_login_2, send_a_message):
    user = register_a_user_then_login_2
    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': json.loads(user.text)['token'],
        'channel_id': -1,
        'start': 0
    })
    assert(resp.status_code == 400)

def test_channel_messages_invalid_start(setup, register_a_user_then_login_2, create_a_channel, send_a_message):
    user = register_a_user_then_login_2
    channel = create_a_channel
    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': json.loads(user.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'start': 600
    })

    assert(resp.status_code == 400)


def test_channel_messages_invalid_successful(setup, register_a_user_then_login_2, create_a_channel, send_a_message):
    user = register_a_user_then_login_2
    channel = create_a_channel
    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': json.loads(user.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'start': 0
    })
    assert(resp.status_code == 200)
   
def test_channel_messages_invalid_successful_1(setup, register_a_user_then_login_2, create_a_channel):
    user = register_a_user_then_login_2
    channel = create_a_channel
    json_text = {
        'token': json.loads(user.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'message': 'weekend'}
    
    # pylint: disable=W0612
    for x in range(51):
        requests.post(config.url + 'message/send/v1', json=json_text)
    
    resp = requests.get(config.url + 'channel/messages/v2', params={
        'token': json.loads(user.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'start': 0
    })
    
    assert(resp.status_code == 200)
