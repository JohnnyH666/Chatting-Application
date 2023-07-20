import pytest
import requests
import json
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

#-------------------user_all_v1_test----------------------
def test_users_all_v1_invalid_token(setup):
    resp = requests.get(config.url + 'users/all/v1', params={'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                                                                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU'})
    assert(resp.status_code == 403)

def test_users_all_invalid_session_id(setup, register_a_user):
    resp_login = requests.post(config.url + 'auth/login/v2',json={
        'email': 'erika@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.get(config.url + 'users/all/v1', params={'token': json.loads(resp_login.text)['token']})
    assert(resp.status_code == 403)

def test_users_all_v1_successfully_1(setup, register_a_user):
    resp_user = register_a_user
    resp = requests.get(config.url + 'users/all/v1', params={'token': json.loads(resp_user.text)['token']})
    assert json.loads(resp.text) == {'users': [{'u_id': 1, 'email': 'erika@gmail.com', 'name_first': 'erika', 'name_last': 'fu', 'handle_str': 'erikafu', 'profile_img_url': ''}]}

def test_users_all_v1_successfully_2(setup, register_a_user, register_a_user1):
    resp_user = register_a_user1
    resp = requests.get(config.url + 'users/all/v1', params={'token': json.loads(resp_user.text)['token']})
    assert json.loads(resp.text) == {'users': [{'u_id': 1, 'email': 'erika@gmail.com', 'name_first': 'erika', 'name_last': 'fu', 'handle_str': 'erikafu', 'profile_img_url': ''},
                                               {'u_id': 2, 'email': 'Yining@gmail.com', 'name_first': 'Yining', 'name_last': 'Zhang', 'handle_str': 'yiningzhang', 'profile_img_url': ''}]}

#-------------------user_profile_v1_test----------------------
def test_user_profile_v1_invalid_token(setup):
    resp = requests.get(config.url + 'user/profile/v1', params={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU',
        'u_id': 666                                                        
    })
    assert(resp.status_code == 403)

def test_user_profile_v1_invalid_u_id(setup):
    resp_user = requests.post(config.url + 'auth/register/v2',
                              json={'email': 'johnny@gmail.com', 
                                    'password': '1234567', 
                                    'name_first': 'johnny', 
                                    'name_last': 'huang'})
    resp = requests.get(config.url + 'user/profile/v1', params={'token': json.loads(resp_user.text)['token'], 'u_id': -1})
    assert(resp.status_code == 400)

def test_users_profile_invalid_session_id(setup, register_a_user):
    resp_login = requests.post(config.url + 'auth/login/v2',json={
        'email': 'erika@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.get(config.url + 'user/profile/v1', params={'token': json.loads(resp_login.text)['token']})
    assert(resp.status_code == 403)
  
def test_user_profile_v1_successful(setup):
    resp_user = requests.post(config.url + 'auth/register/v2',
                              json={'email': 'johnny@gmail.com', 
                                    'password': '1234567', 
                                    'name_first': 'johnny', 
                                    'name_last': 'huang'})
    resp = requests.get(config.url + 'user/profile/v1', params={'token': json.loads(resp_user.text)['token'], 'u_id': 1})
    assert json.loads(resp.text) ==  {'user': {'email': 'johnny@gmail.com',
                                               'handle_str': 'johnnyhuang',
                                               'name_first': 'johnny',
                                               'name_last': 'huang',
                                               'u_id': 1,
                                               'profile_img_url': ''}}

#-------------------user_profile_setname_v1_test----------------------
def test_user_profile_setname_v1_invalid_token_1(setup):
    resp = requests.put(config.url + 'user/profile/setname/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU',
        'name_first': 'Linlin', 
        'name_last': 'Luo' })
    assert(resp.status_code == 403)

def test_user_profile_setname_v1_invalid_token_2(setup, register_a_user3):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Libo@gmail.com', 
        'password': '1234567'})
    
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']})
    
    resp_setname = requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(resp_login.text)['token'],
        'name_first': 'Linlin',
        'name_last': 'Luo'})
    
    assert(resp_setname.status_code == 403)

def test_user_profile_setname_v1_first_wrong_length_1(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user3.text)['token'], 
        'name_first': 'Linlin'*100, 
        'name_last': 'Luo'})
    assert(resp.status_code == 400)

def test_user_profile_setname_v1_first_wrong_length_2(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user3.text)['token'], 
        'name_first': '', 
        'name_last': 'Luo'})
    assert(resp.status_code == 400)

def test_user_profile_setname_v1_last_wrong_length_1(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user3.text)['token'],  
        'name_first': 'Linlin', 
        'name_last': 'Luo'*100})
    assert(resp.status_code == 400)

def test_user_profile_setname_v1_last_wrong_length_2(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user3.text)['token'],  
        'name_first': 'Linlin', 
        'name_last': ''})
    assert(resp.status_code == 400)

def test_user_profile_setname_v1_first_and_last_wrong_length_1(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user3.text)['token'],  
        'name_first': 'Linlin'*100, 
        'name_last': 'Luo'*108})
    assert(resp.status_code == 400)

def test_user_profile_setname_v1_first_and_last_wrong_length_2(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user3.text)['token'],  
        'name_first': '', 
        'name_last': ''})
    assert(resp.status_code == 400)

def test_user_profile_setname_v1_first_and_last_wrong_length_3(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user3.text)['token'],  
        'name_first': 'Linlin'*100, 
        'name_last': ''})
    assert(resp.status_code == 400)

def test_user_profile_setname_v1_first_and_last_wrong_length_4(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user3.text)['token'],  
        'name_first': '', 
        'name_last': 'Luo'*100})
    assert(resp.status_code == 400)

def test_user_profile_setname_v1_successful_1(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user3.text)['token'],  
        'name_first': 'Linlin', 
        'name_last': 'Luo'})
    assert(resp.status_code == 200)

def test_user_profile_setname_v1_successful_2(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })

    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user1.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id']
    }) 
  
       
    requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user1.text)['token'],  
        'name_first': 'Linlin', 
        'name_last': 'Luo'})

    resp = requests.get(config.url + 'channel/details/v2', params={
        'token': json.loads(user3.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })

    assert json.loads(resp.text) == {'name': 'love', 'is_public': True, 
    'owner_members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'}],
    'all_members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'}, 
    {'u_id': 2, 'handle_str': 'yiningzhang', 'email': 'Yining@gmail.com', 'name_first': 'Linlin', 'name_last': 'Luo'}]} 

def test_user_profile_setname_v1_fail_1(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })
  
       
    requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user1.text)['token'],  
        'name_first': 'Linlin', 
        'name_last': 'Luo'})

    resp = requests.get(config.url + 'channel/details/v2', params={
        'token': json.loads(user1.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })
    
    assert resp.status_code == 403


def test_user_profile_setname_v1_successful_3(setup, register_a_user2, register_a_user3):
    user3 = register_a_user3

    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })

    user2 = register_a_user2
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id']
    })                                                                              
    requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(user3.text)['token'], 
        'channel_id': json.loads(channel1.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    
    requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user3.text)['token'],  
        'name_first': 'Linlin', 
        'name_last': 'Luo'})
       

    resp = requests.post(config.url + 'channel/leave/v1', json={
        'token': json.loads(user3.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })

    assert(resp.status_code == 200)

def test_user_profile_setname_v1_fail_2(setup, register_a_user3, register_a_user1 ):
    user3 = register_a_user3
    user1 = register_a_user1
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })
    
    requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user1.text)['token'],  
        'name_first': 'Linlin', 
        'name_last': 'Luo'})
       

    resp = requests.post(config.url + 'channel/leave/v1', json={
        'token': json.loads(user1.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })

    assert(resp.status_code == 403)

def test_user_profile_setname_v1_successful_4(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    dm1 = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user3.text)['token'],
        'u_ids': [json.loads(user1.text)['auth_user_id']] })
  
    requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user1.text)['token'],  
        'name_first': 'Linlin', 
        'name_last': 'Luo'})

    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': json.loads(user1.text)['token'],
        'dm_id': json.loads(dm1.text)['dm_id'] })

    assert(json.loads(resp.text) == {'name': 'libocheng, yiningzhang',
        'members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'}, 
        {'u_id': 2, 'handle_str': 'yiningzhang', 'email': 'Yining@gmail.com', 'name_first': 'Linlin', 'name_last': 'Luo'}] })

def test_user_profile_setname_v1_fail_3(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    dm1 = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user3.text)['token'],
        'u_ids': [] })
  
    requests.put(config.url + 'user/profile/setname/v1', json={
        'token': json.loads(user1.text)['token'],  
        'name_first': 'Linlin', 
        'name_last': 'Luo'})

    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': json.loads(user1.text)['token'],
        'dm_id': json.loads(dm1.text)['dm_id'] })

    assert(resp.status_code == 403)

#-------------------user_profile_setemail_v1_test----------------------
def test_user_profile_setemail_v1_invalid_token_1(setup):
    resp = requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU',
        'email': 'Linlin@gmail.com' })
    assert(resp.status_code == 403)

def test_user_profile_setemail_v1_invalid_token_2(setup, register_a_user3):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Libo@gmail.com', 
        'password': '1234567'})
    
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']})
    
    resp_setemail = requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': json.loads(resp_login.text)['token'],
        'email': 'Linlin@gmail.com'})
    
    assert(resp_setemail.status_code == 403)

def test_user_profile_setemail_v1_invalid_email(setup,register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': json.loads(user3.text)['token'],
        'email': 'invalid email'})
                               
    assert(resp.status_code == 400)

def test_user_profile_setemail_v1_existed_email_1(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': json.loads(user3.text)['token'],
        'email': 'Libo@gmail.com'})
    
    assert(resp.status_code == 400)

def test_user_profile_setemail_v1_existed_email_2(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    register_a_user1
    resp = requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': json.loads(user3.text)['token'],
        'email': 'Yining@gmail.com'})
    
    assert(resp.status_code == 400)

def test_user_profile_setemail_v1_successful_1(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': json.loads(user3.text)['token'],
        'email': 'Linlin@gmail.com'})
    
    assert(resp.status_code == 200)

def test_user_profile_setemail_v1_successful_2(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })
  
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user1.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id']
    }) 

    requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': json.loads(user1.text)['token'],  
        'email': 'Linlin@gmail.com'})
        
    resp = requests.get(config.url + 'channel/details/v2', params={
        'token': json.loads(user3.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })

    assert json.loads(resp.text) == {'name': 'love', 'is_public': True, 
    'owner_members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'}],
    'all_members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'}, 
    {'u_id': 2, 'handle_str': 'yiningzhang', 'email': 'Linlin@gmail.com', 'name_first': 'Yining', 'name_last': 'Zhang'}]} 

def test_user_profile_setemail_v1_fail_1(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })
  
       
    requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': json.loads(user1.text)['token'],  
        'email': 'Linlin@gmail.com'})
        
    resp = requests.get(config.url + 'channel/details/v2', params={
        'token': json.loads(user1.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })

    assert(resp.status_code == 403)

def test_user_profile_setemail_v1_successful_3(setup, register_a_user2, register_a_user3):
    user3 = register_a_user3
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })
    
    user2 = register_a_user2
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id']
    })                                                                              
    requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(user3.text)['token'], 
        'channel_id': json.loads(channel1.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })   

    requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': json.loads(user3.text)['token'], 
        'email': 'Linlin@gmail.com'})
       

    resp = requests.post(config.url + 'channel/leave/v1', json={
        'token': json.loads(user3.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })

    assert(resp.status_code == 200)

def test_user_profile_setemail_v1_fail_2(setup, register_a_user3,  register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })
    
    requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': json.loads(user1.text)['token'], 
        'email': 'Linlin@gmail.com'})
       

    resp = requests.post(config.url + 'channel/leave/v1', json={
        'token': json.loads(user1.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })

    assert(resp.status_code == 403)


def test_user_profile_setemail_v1_successful_4(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    dm1 = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user3.text)['token'],
        'u_ids': [json.loads(user1.text)['auth_user_id']] })
  
    requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': json.loads(user1.text)['token'],  
        'email': 'Linlin@gmail.com'})

    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': json.loads(user1.text)['token'],
        'dm_id': json.loads(dm1.text)['dm_id'] })

    assert(json.loads(resp.text) == {'name': 'libocheng, yiningzhang',
        'members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'}, 
        {'u_id': 2, 'handle_str': 'yiningzhang', 'email': 'Linlin@gmail.com', 'name_first': 'Yining', 'name_last': 'Zhang'}] })
    
def test_user_profile_setemail_v1_fail_3(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    dm1 = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user3.text)['token'],
        'u_ids': [] })
  
    requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': json.loads(user1.text)['token'],  
        'email': 'Linlin@gmail.com'})

    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': json.loads(user1.text)['token'],
        'dm_id': json.loads(dm1.text)['dm_id'] })

    assert(resp.status_code == 403)
#-------------------user_profile_sethandle_v1_test----------------------
def test_user_profile_sethandle_v1_invalid_token_1(setup):
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
        'handle_str': 'jskhxka'})
    assert(resp.status_code == 403)

def test_user_profile_sethandle_v1_invalid_token_2(setup, register_a_user3):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Libo@gmail.com', 
        'password': '1234567'})
    
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']})
    
    resp_sethandle = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(resp_login.text)['token'],
        'handle_str': 'linlinluo'})
    
    assert(resp_sethandle.status_code == 403)

def test_user_profile_sethandle_v1_invalid_handle_str_invalid_length_1(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': 'libo'*100})
                               
    assert(resp.status_code == 400)

def test_user_profile_sethandle_v1_invalid_handle_str_invalid_length_2(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': ''})
                               
    assert(resp.status_code == 400)

def test_user_profile_sethandle_v1_invalid_handle_str_invalid_length_3(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': 'li'})
                               
    assert(resp.status_code == 400)

def test_user_profile_sethandle_v1_invalid_handle_str_invalid_characters_1(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': '@&#]'})
                               
    assert(resp.status_code == 400)

def test_user_profile_sethandle_v1_invalid_handle_str_invalid_characters_2(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': 'li2K~/MHi>oio#]'})
                               
    assert(resp.status_code == 400)

def test_user_profile_sethandle_v1_invalid_handle_str_existed_handle_1(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': 'libocheng'})
                               
    assert(resp.status_code == 400)

def test_user_profile_sethandle_v1_invalid_handle_str_existed_handle_2(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    register_a_user1
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': 'yiningzhang'})
                               
    assert(resp.status_code == 400)

def test_user_profile_sethandle_v1_invalid_handle_str_invalid_characters_and_invalid_length(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': 'L@'})
                               
    assert(resp.status_code == 400)

def test_user_profile_sethandle_v1_valid_handle_str_successful_1(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': 'yiningzhang'})
                               
    assert(resp.status_code == 200)

def test_user_profile_sethandle_v1_valid_handle_str_successful_2(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': '1234'})
                               
    assert(resp.status_code == 200)

def test_user_profile_sethandle_v1_valid_handle_str_successful_3(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': '1L9i'})
                               
    assert(resp.status_code == 200)

def test_user_profile_sethandle_v1_valid_handle_str_successful_4(setup, register_a_user3):
    user3 = register_a_user3
    resp = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': 'LINLINLUO'})
                               
    assert(resp.status_code == 200)

def test_user_profile_sethandle_v1_successful_5(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })

    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user1.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id']
    }) 
  
       
    requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user1.text)['token'],  
        'handle_str': 'linlinluo'})
        
    resp = requests.get(config.url + 'channel/details/v2', params={
        'token': json.loads(user3.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })

    assert json.loads(resp.text) == {'name': 'love', 'is_public': True, 
    'owner_members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'}],
    'all_members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'}, 
    {'u_id': 2, 'handle_str': 'linlinluo', 'email': 'Yining@gmail.com', 'name_first': 'Yining', 'name_last': 'Zhang'}]} 

def test_user_profile_sethandle_v1_fail_1(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })
  
       
    requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user1.text)['token'],  
        'handle_str': 'linlinluo'})
        
    resp = requests.get(config.url + 'channel/details/v2', params={
        'token': json.loads(user1.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })

    assert(resp.status_code == 403)

def test_user_profile_sethandle_v1_successful_6(setup, register_a_user2, register_a_user3):
    user3 = register_a_user3
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })
    
    user2 = register_a_user2
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id']
    })                                                                              
    requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(user3.text)['token'], 
        'channel_id': json.loads(channel1.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    
    requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user3.text)['token'], 
        'handle_str': 'linlinluo'})
       

    resp = requests.post(config.url + 'channel/leave/v1', json={
        'token': json.loads(user3.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })

    assert(resp.status_code == 200)

def test_user_profile_sethandle_v1_fail_2(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })
    
    requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user1.text)['token'], 
        'handle_str': 'linlinluo'})
       

    resp = requests.post(config.url + 'channel/leave/v1', json={
        'token': json.loads(user1.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })

    assert(resp.status_code == 403)

def test_user_profile_sethandle_v1_successful_7(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    dm1 = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user3.text)['token'],
        'u_ids': [json.loads(user1.text)['auth_user_id']] })
  
    requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user1.text)['token'],  
        'handle_str': 'linlinluo'})

    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': json.loads(user1.text)['token'],
        'dm_id': json.loads(dm1.text)['dm_id'] })

    assert(json.loads(resp.text) == {'name': 'libocheng, yiningzhang',
        'members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'}, 
        {'u_id': 2, 'handle_str': 'linlinluo', 'email': 'Yining@gmail.com', 'name_first': 'Yining', 'name_last': 'Zhang'}] })
    
def test_user_profile_sethandle_v1_fail_3(setup, register_a_user3, register_a_user1):
    user3 = register_a_user3
    user1 = register_a_user1
    dm1 = requests.post(config.url + 'dm/create/v1', json={
        'token': json.loads(user3.text)['token'],
        'u_ids': [] })
  
    requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': json.loads(user1.text)['token'],  
        'handle_str': 'linlinluo'})

    resp = requests.get(config.url + 'dm/details/v1', params={
        'token': json.loads(user1.text)['token'],
        'dm_id': json.loads(dm1.text)['dm_id'] })

    assert(resp.status_code == 403)

#-------------------admin_userpermission_change_v1_test----------------------
def test_admin_userpermission_change_v1_invalid_token(setup):
    resp = requests.post(config.url + 'admin/userpermission/change/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
        'u_id': 666, 
        'permission_id': 1
    })
    assert(resp.status_code == 403)

def test_admin_userpermission_change_v1_invalid_session(setup, register_a_user1, register_a_user2):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.post(config.url + 'admin/userpermission/change/v1',
                              json={'token': json.loads(resp_login.text)['token'], 
                                    'u_id': 1, 
                                    'permission_id': 1})
    assert(resp.status_code == 403)

def test_admin_userpermission_change_not_global_owner(setup, register_a_user, register_a_user1):
    resp_user_2 = register_a_user1
    resp = requests.post(config.url + 'admin/userpermission/change/v1',
                              json={'token': json.loads(resp_user_2.text)['token'], 
                                    'u_id': 1, 
                                    'permission_id': 1})
    assert(resp.status_code == 403)

def test_admin_userpermission_change_v1_invalid_id(setup, register_a_user):
    resp_user = register_a_user 
    resp = requests.post(config.url + 'admin/userpermission/change/v1',
                              json={'token': json.loads(resp_user.text)['token'], 
                                    'u_id': -1, 
                                    'permission_id': 1})
    assert(resp.status_code == 400)

def test_admin_userpermission_change_only_global_owner_demoted_user(setup, register_a_user):
    resp_user = register_a_user
    resp = requests.post(config.url + 'admin/userpermission/change/v1',
                              json={'token': json.loads(resp_user.text)['token'], 
                                    'u_id': 1, 
                                    'permission_id': 2})
    assert(resp.status_code == 400)

def test_admin_userpermission_change_invalid_permission_id(setup, register_a_user):
    resp_user = register_a_user
    resp = requests.post(config.url + 'admin/userpermission/change/v1',
                              json={'token': json.loads(resp_user.text)['token'], 
                                    'u_id': 1, 
                                    'permission_id': 3})
    assert(resp.status_code == 400)

def test_admin_userpermission_change_successful(setup, register_a_user, register_a_user2):
    resp_user = register_a_user
    resp_user2 = register_a_user2
    resp = requests.post(config.url + 'admin/userpermission/change/v1',
                              json={'token': json.loads(resp_user.text)['token'], 
                                    'u_id': json.loads(resp_user2.text)['auth_user_id'], 
                                    'permission_id': 1}) 
    
    resp = requests.post(config.url + 'admin/userpermission/change/v1',
                              json={'token': json.loads(resp_user2.text)['token'], 
                                    'u_id': json.loads(resp_user.text)['auth_user_id'], 
                                    'permission_id': 2}) 
    assert(resp.status_code == 200)  

#-------------------admin_user_remove_v1_test----------------------
def test_admin_remove_v1_invalid_token(setup):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU',
        'u_id': 666
    })
    assert(resp.status_code == 403)

def test_admin_remove_v1_invalid_session(setup, register_a_user1, register_a_user2):
    user2 = register_a_user2
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': json.loads(resp_login.text)['token'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })
    assert(resp.status_code == 403)

def test_admin_remove_v1_auth_not_globalowner(setup, register_a_user1, register_a_user2):
    user2 = register_a_user2
    user3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'hello@gmail.com', 
        'password': '1234567', 
        'name_first': 'Yining', 
        'name_last': 'Zhang'
    })
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': json.loads(user2.text)['token'],
        'u_id': json.loads(user3.text)['auth_user_id']
    })
    assert(resp.status_code == 403)

def test_admin_remove_v1_invalid_u_id(setup, register_a_user1):
    user1 = register_a_user1   
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': json.loads(user1.text)['token'],
        'u_id': 666
    })
    assert(resp.status_code == 400)    

def test_admin_remove_v1_only_globalowner(setup, register_a_user1):
    user1 = register_a_user1   
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': json.loads(user1.text)['token'],
        'u_id': json.loads(user1.text)['auth_user_id']
    })
    assert(resp.status_code == 400)       

def test_admin_remove_v1_success(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1 
    user2 = register_a_user2
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': json.loads(user1.text)['token'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })
    assert(resp.status_code == 200)  

def test_admin_remove_v1_success2(setup, register_a_user1, register_a_user2, register_a_user3):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
    'token': json.loads(user1.text)['token'], 
    'name': 'happy', 
    'is_public': True
    })
    user2 = register_a_user2
    requests.post(config.url + 'channels/create/v2', json={
    'token': json.loads(user2.text)['token'], 
    'name': 'cool', 
    'is_public': True
    })
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    })
    requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'message': 'have a good day'
    }) 
    user3 = register_a_user3
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user3.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    }) 
    requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user3.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'message': 'cool'
    }) 
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': json.loads(user1.text)['token'],
        'u_id': json.loads(user3.text)['auth_user_id']
    })
    assert(resp.status_code == 200)  

def test_admin_remove_v1_success3(setup, register_a_user1, register_a_user2, register_a_user3, register_a_user):
    user1 = register_a_user1 
    user2 = register_a_user2
    requests.post(config.url + 'dm/create/v1', json={ 
        'token': json.loads(user1.text)['token'], 
        'u_ids': [json.loads(user2.text)['auth_user_id']]
    })
    user3 = register_a_user3
    user4 = register_a_user
    requests.post(config.url + 'dm/create/v1', json={ 
        'token': json.loads(user3.text)['token'], 
        'u_ids': [json.loads(user4.text)['auth_user_id'], json.loads(user3.text)['auth_user_id']]
    })
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': json.loads(user1.text)['token'],
        'u_id': json.loads(user3.text)['auth_user_id']
    })
    assert(resp.status_code == 200)  

def test_admin_remove_v1_success4(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1 
    user2 = register_a_user2
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user2.text)['token'], 
        'name': 'happy', 
        'is_public': False
    })
    resp = requests.post(config.url + 'message/send/v1', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id'],
        'message': 'have a good day'
    })

    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': json.loads(user1.text)['token'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })
    assert(resp.status_code == 200)  


def test_once_removed_user_cant_do_anything(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1 
    user2 = register_a_user2
    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': json.loads(user1.text)['token'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })
    resp = requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(user2.text)['token']
    })
    
    assert(resp.status_code == 403) 
     
def test_removal_not_in_users_all(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1 
    user2 = register_a_user2
    requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': json.loads(user1.text)['token'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })
    resp = requests.get(config.url + 'users/all/v1', params={'token': json.loads(user1.text)['token']})
    users = json.loads(resp.text)['users']
    assert json.loads(user2.text)['auth_user_id'] not in [u['u_id'] for u in users]