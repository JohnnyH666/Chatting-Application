import pytest
import requests
import json
from src import config

@pytest.fixture
def setup():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register_a_user1():
    return requests.post(config.url + 'auth/register/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567', 
        'name_first': 'Yining', 
        'name_last': 'Zhang'})

@pytest.fixture
def register_a_user2():
    return requests.post(config.url + 'auth/register/v2', json={
        'email': 'Zhang@gmail.com', 
        'password': '1234567', 
        'name_first': 'Yining', 
        'name_last': 'Zhang'})

@pytest.fixture
def register_a_user3():
    return requests.post(config.url + 'auth/register/v2', json={
        'email': 'Libo@gmail.com', 
        'password': '1234567', 
        'name_first': 'Libo', 
        'name_last': 'Cheng'})

@pytest.fixture
def register_a_user4():
    return requests.post(config.url + 'auth/register/v2', json={
        'email': 'Linlin@gmail.com', 
        'password': '1234567', 
        'name_first': 'Linlin', 
        'name_last': 'Luo'})
                           
#-------------------dm_create_v1_test----------------------
def test_dm_create_invalid_token(setup):
    resp = requests.post(config.url + 'dm/create/v1',
                        json={'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                                       'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
                              'u_ids': []})
    assert(resp.status_code == 403)

#AccessError - invalid session
def test_dm_create_invalid_session(setup, register_a_user1):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(resp_login.text)['token'], 
        'u_ids': []
    }) 
    assert(resp.status_code == 403)

def test_dm_create_invalid_id(setup):
    resp_user = requests.post(config.url + 'auth/register/v2',
                              json={'email': 'johnny@gmail.com', 
                                    'password': '1234567', 
                                    'name_first': 'johnny', 
                                    'name_last': 'huang'})
    resp = requests.post(config.url + 'dm/create/v1',
                         json={'token': json.loads(resp_user.text)['token'], 
                               'u_ids': [2, 3]})
    assert(resp.status_code == 400)

def test_dm_create_empty_list(setup):
    resp_user = requests.post(config.url + 'auth/register/v2',
                              json={'email': 'johnny@gmail.com', 
                                    'password': '1234567', 
                                    'name_first': 'johnny', 
                                    'name_last': 'huang'})
    resp = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(resp_user.text)['token'], 
                               'u_ids': []})
    assert json.loads(resp.text) == {'dm_id': 1}

def test_dm_create_successful(setup):
    resp_user = requests.post(config.url + 'auth/register/v2',
                              json={'email': 'johnny@gmail.com', 
                                    'password': '1234567', 
                                    'name_first': 'johnny', 
                                    'name_last': 'huang'})                           
    resp = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(resp_user.text)['token'], 
                               'u_ids': [1]})
    assert json.loads(resp.text) == {'dm_id': 1}

def test_dm_create_successful_2():
    resp_user_2 = requests.post(config.url + 'auth/register/v2',
                                json={'email': 'erika@gmail.com', 
                                        'password': '1234567', 
                                        'name_first': 'erika', 
                                        'name_last': 'fu'
                                        })                              
    resp = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(resp_user_2.text)['token'], 
                               'u_ids': [2]})
    assert json.loads(resp.text) == {'dm_id': 2}

#-------------------dm_list_v1_test----------------------
def test_dm_list_invalid_token(setup):
    resp = requests.get(config.url + 'dm/list/v1', params={'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                                                                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU'})
    assert(resp.status_code == 403)

def test_dm_list_invalid_session(setup, register_a_user1):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.get(config.url + 'dm/list/v1', params={'token': json.loads(resp_login.text)['token']})
    assert(resp.status_code == 403)

def test_dm_list_empty_list(setup):
    resp_user = requests.post(config.url + 'auth/register/v2',
                              json={'email': 'johnny@gmail.com', 
                                    'password': '1234567', 
                                    'name_first': 'johnny', 
                                    'name_last': 'huang'})
    resp = requests.get(config.url + 'dm/list/v1', params={'token': json.loads(resp_user.text)['token']})
    assert json.loads(resp.text)['dms'] == []


def test_dm_list_successfully(setup):
    resp_user = requests.post(config.url + 'auth/register/v2',
                              json={'email': 'johnny@gmail.com', 
                                    'password': '1234567', 
                                    'name_first': 'johnny', 
                                    'name_last': 'huang'})
    requests.post(config.url + 'auth/register/v2',
                json={'email': 'erika@gmail.com', 
                        'password': '1234567', 
                        'name_first': 'erika', 
                        'name_last': 'fu'
                        })   

    requests.post(config.url + 'dm/create/v1', 
                json={'token': json.loads(resp_user.text)['token'], 
                    'u_ids': [2]})
    resp_list = requests.get(config.url + 'dm/list/v1', params={'token': json.loads(resp_user.text)['token']})
    assert json.loads(resp_list.text) == {'dms': [{'dm_id': 1, 'name': 'erikafu, johnnyhuang'}]}
    

#-------------------dm_leave_v1_test---------------------- 

#AccessError - the token passed in is invalid
def test_dm_leave_invalid_token(setup):
    resp = requests.post(config.url + 'dm/leave/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
        'dm_id': 5
    })   
    assert(resp.status_code == 403)

#invalid session
def test_dm_leave_invalid_session(setup, register_a_user1, register_a_user2):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.post(config.url + 'dm/leave/v1', json={
        'token': json.loads(resp_login.text)['token'], 
        'dm_id': 666
    }) 
    assert(resp.status_code == 403)

#AccessError - dm_id is valid and the authorised user is not a member of the DM
def test_dm_leave_not_member_of_dm(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    dm = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user1.text)['token'], 
        'u_ids': [1]
    })
    user2 = register_a_user2
    resp = requests.post(config.url + 'dm/leave/v1', json={
        'token': json.loads(user2.text)['token'], 
        'dm_id': json.loads(dm.text)['dm_id']
    })   
    assert(resp.status_code == 403)    

#InputError - dm_id does not refer to a valid DM
def test_dm_leave_invalid_dm(setup, register_a_user1):
    user1 = register_a_user1
    resp = requests.post(config.url + 'dm/leave/v1', json={
        'token': json.loads(user1.text)['token'], 
        'dm_id': 666
    })   
    assert(resp.status_code == 400)  

#leave success
def test_dm_leave_success_1(setup, register_a_user1, register_a_user3):
    user1 = register_a_user1
    user3 = register_a_user3
    dm = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user1.text)['token'], 
        'u_ids': [json.loads(user3.text)['auth_user_id']]
    })
    resp = requests.post(config.url + 'dm/leave/v1', json={
        'token': json.loads(user1.text)['token'], 
        'dm_id': json.loads(dm.text)['dm_id']
    })   
    assert(resp.status_code == 200)

def test_dm_leave_success_2(setup, register_a_user1, register_a_user3):
    user1 = register_a_user1
    user3 = register_a_user3
    dm = requests.post(config.url + 'dm/create/v1', json={ 
        'token': json.loads(user1.text)['token'], 
        'u_ids': [json.loads(user3.text)['auth_user_id']]
    })
    resp = requests.post(config.url + 'dm/leave/v1', json={
        'token': json.loads(user3.text)['token'], 
        'dm_id': json.loads(dm.text)['dm_id']
    })   
    assert(resp.status_code == 200)

#------------------- dm_messages_v1 test ---------------------- 
def test_dm_message_invalid_token_1(setup):
    resp = requests.get(config.url + 'dm/messages/v1',params={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU',
        'dm_id': 5,
        'start': 0})   
    assert(resp.status_code == 403)

def test_dm_message_invalid_token_2(setup, register_a_user1):
    user = register_a_user1
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(user.text)['token']
    })
    resp = requests.get(config.url + 'dm/messages/v1',params={
        'token': json.loads(user.text)['token'],
        'dm_id': 5,
        'start': 0})   
    assert(resp.status_code == 403)

def test_dm_message_not_a_member(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    dm = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(user1.text)['token'], 
                               'u_ids': []})
    user2 = register_a_user2
    resp = requests.get(config.url + 'dm/messages/v1',params={
        'token': json.loads(user2.text)['token'], 
        'dm_id': json.loads(dm.text)['dm_id'],
        'start': 0})   
    assert(resp.status_code == 403)

def test_dm_message_invalid_dm_id(setup, register_a_user1):
    user1 = register_a_user1
    resp = requests.get(config.url + 'dm/messages/v1',params={
        'token': json.loads(user1.text)['token'], 
        'dm_id': -1,
        'start': 0})   
    assert(resp.status_code == 400)  

def test_dm_message_invalid_start(setup, register_a_user1):
    user1 = register_a_user1
    dm = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(user1.text)['token'], 
                               'u_ids': []})
    resp = requests.get(config.url + 'dm/messages/v1',params={
        'token': json.loads(user1.text)['token'], 
        'dm_id': json.loads(dm.text)['dm_id'],
        'start': 100})   
    assert(resp.status_code == 400)

def test_dm_message_successful_1(setup, register_a_user1):
    user1 = register_a_user1
    dm = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(user1.text)['token'], 
                               'u_ids': []})

    requests.post(config.url + 'message/senddm/v1',json={
        'token': json.loads(user1.text)['token'],
        'dm_id': json.loads(dm.text)['dm_id'],
        'message': 'weekend'})   

    resp = requests.get(config.url + 'dm/messages/v1',params={
        'token': json.loads(user1.text)['token'], 
        'dm_id': json.loads(dm.text)['dm_id'],
        'start': 0})   
    assert(resp.status_code == 200)
    assert(json.loads(resp.text)['start'] == 0)
    assert(json.loads(resp.text)['end'] == -1)

def test_dm_message_successful_2(setup, register_a_user1):
    user1 = register_a_user1
    dm = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(user1.text)['token'], 
                               'u_ids': []})
    
    json_text = {
        'token': json.loads(user1.text)['token'],
        'dm_id': json.loads(dm.text)['dm_id'],
        'message': 'weekend'}
    
    dm_ids = []
    # pylint: disable=W0612
    for x in range(51): 
        id = requests.post(config.url + 'message/senddm/v1',json=json_text)
        dm_ids.append(json.loads(id.text)['message_id']) 
    dm_ids.reverse() 
    
    resp = requests.get(config.url + 'dm/messages/v1',params={
        'token': json.loads(user1.text)['token'], 
        'dm_id': json.loads(dm.text)['dm_id'],
        'start': 0})   
    assert(resp.status_code == 200)
    assert(json.loads(resp.text)['start'] == 0)
    assert(json.loads(resp.text)['end'] == 50)
    dm_msgs = json.loads(resp.text)['messages']
    assert(dm_ids == [m['message_id'] for m in dm_msgs])

#------------------- message_senddm_v1 test ---------------------- 
def test_message_senddm_invalid_token_1(setup):
    resp = requests.post(config.url + 'message/senddm/v1',json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU',
        'dm_id': 5,
        'message': 'weekend'})   
    assert(resp.status_code == 403)

def test_message_senddm_invalid_token_2(setup, register_a_user1):
    user = register_a_user1
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(user.text)['token']
    })
    resp = requests.post(config.url + 'message/senddm/v1',json={
        'token': json.loads(user.text)['token'],
        'dm_id': 5,
        'message': 'weekend'})   
    assert(resp.status_code == 403)

def test_message_senddm_not_a_member(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    dm = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(user1.text)['token'], 
                               'u_ids': []})
    user2 = register_a_user2
    resp = requests.post(config.url + 'message/senddm/v1',json={
        'token': json.loads(user2.text)['token'],
        'dm_id': json.loads(dm.text)['dm_id'],
        'message': 'weekend'})   
    assert(resp.status_code == 403)


def test_message_senddm_invalid_dm(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    resp = requests.post(config.url + 'message/senddm/v1',json={
        'token': json.loads(user1.text)['token'],
        'dm_id': -1,
        'message': 'weekend'})   
    assert(resp.status_code == 400)

def test_message_senddm_invalid_length(setup, register_a_user1):
    user1 = register_a_user1
    dm = requests.post(config.url + 'dm/create/v1', 
                         json={'token': json.loads(user1.text)['token'], 
                               'u_ids': []})
    resp = requests.post(config.url + 'message/senddm/v1',json={
        'token': json.loads(user1.text)['token'],
        'dm_id': json.loads(dm.text)['dm_id'],
        'message': 'weekend'*9000})   
    assert(resp.status_code == 400)

def test_message_senddm_successful(setup, register_a_user1):
    user1 = register_a_user1
    dm = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user1.text)['token'], 
        'u_ids': []})
    resp = requests.post(config.url + 'message/senddm/v1',json={
        'token': json.loads(user1.text)['token'],
        'dm_id': json.loads(dm.text)['dm_id'],
        'message': 'weekend'})   
    assert(resp.status_code == 200)
    assert (json.loads(resp.text)['message_id'] == 0)

#-------------------dm_remove_v1_test----------------------
# Test if AccessError occurs when token and dm_id are invalid
def test_dm_remove_invalid_token(setup):
    resp = requests.delete(config.url + 'dm/remove/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
        'dm_id': 3})   
    assert(resp.status_code == 403)

def test_dm_remove_invalid_session(setup, register_a_user1):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.delete(config.url + 'dm/remove/v1', json={
        'token': json.loads(resp_login.text)['token'],
        'dm_id': 1234
    })
    assert(resp.status_code == 403)

# Test if InputError occurs when dm_id is invalid and token is valid 
def test_dm_remove_valid_token_and_invalid_channel_id(setup, register_a_user4):
    user4 = register_a_user4
    resp = requests.delete(config.url + 'dm/remove/v1', json={
        'token': json.loads(user4.text)['token'],
        'dm_id': 1234})
    assert(resp.status_code == 400)

# Test if AccessError occurs when the authorised user is not the original DM creator 
def test_dm_remove_invalid_user(setup, register_a_user3, register_a_user4):
    user3 = register_a_user3  
    dm1 = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user3.text)['token'],
        'u_ids': [] })
    user4 = register_a_user4
    resp = requests.delete(config.url + 'dm/remove/v1', json={
        'token': json.loads(user4.text)['token'],
        'dm_id': json.loads(dm1.text)['dm_id']})
    assert(resp.status_code == 403)

# Test if provide successful
def test_dm_remove_sucesssful(setup, register_a_user3, register_a_user4):
    user3 = register_a_user3
    user4 = register_a_user4  
    dm1 = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user3.text)['token'],
        'u_ids': [json.loads(user4.text)['auth_user_id']] })
    resp = requests.delete(config.url + 'dm/remove/v1', json={
        'token': json.loads(user3.text)['token'],
        'dm_id': json.loads(dm1.text)['dm_id'] })
    assert(resp.status_code == 200)


#-------------------dm_details_v1_test----------------------
# Test if AccessError occurs when token and dm_id are invalid
def test_dm_details_invalid_token(setup):
    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
        'dm_id': 3})   
    assert(resp.status_code == 403)

def test_dm_details_invalid_session(setup, register_a_user1):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': json.loads(resp_login.text)['token'],
        'dm_id': 1234
    })
    assert(resp.status_code == 403)

# Test if InputError occurs when dm_id is invalid and token is valid 
def test_dm_deatils_valid_token_and_invalid_channel_id(setup, register_a_user4):
    user4 = register_a_user4
    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': json.loads(user4.text)['token'],
        'dm_id': 1234})
    assert(resp.status_code == 400)

# Test if AccessError occurs when the authorised user is not the member of DM 
def test_dm_details_invalid_user(setup, register_a_user3, register_a_user4):
    user3 = register_a_user3  
    dm1 = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user3.text)['token'],
        'u_ids': [] })
    user4 = register_a_user4
    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': json.loads(user4.text)['token'],
        'dm_id': json.loads(dm1.text)['dm_id']})
    assert(resp.status_code == 403)

# Test if provide successful
def test_dm_details_sucesssful_1(setup, register_a_user3, register_a_user4):
    user3 = register_a_user3 
    user4 = register_a_user4
    dm1 = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user3.text)['token'],
        'u_ids': [json.loads(user4.text)['auth_user_id']] })
    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': json.loads(user3.text)['token'],
        'dm_id': json.loads(dm1.text)['dm_id'] })
    assert(json.loads(resp.text) == {'name': 'libocheng, linlinluo',
        'members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'},
        {'u_id': 2, 'handle_str': 'linlinluo', 'email': 'Linlin@gmail.com', 'name_first': 'Linlin', 'name_last': 'Luo'}] })

def test_dm_details_sucesssful_2(setup, register_a_user3, register_a_user4):
    user3 = register_a_user3 
    user4 = register_a_user4
    dm1 = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user3.text)['token'],
        'u_ids': [json.loads(user4.text)['auth_user_id']] })
    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': json.loads(user4.text)['token'],
        'dm_id': json.loads(dm1.text)['dm_id'] })
    assert(json.loads(resp.text) == {'name': 'libocheng, linlinluo',
        'members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'},
        {'u_id': 2, 'handle_str': 'linlinluo', 'email': 'Linlin@gmail.com', 'name_first': 'Linlin', 'name_last': 'Luo'}] })
