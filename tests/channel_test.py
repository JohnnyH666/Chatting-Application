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



#-------------------channel_join_v2_test----------------------

#AccessError - the token passed in is invalid
def test_channel_join_invalid_token(setup):
    resp = requests.post(config.url + 'channel/join/v2', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
        'channel_id': 3
    })   
    assert(resp.status_code == 403)

#AccessError - invalid session
def test_channel_join_invalid_session(setup, register_a_user1):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(resp_login.text)['token'],
        'channel_id': 666
    }) 
    assert(resp.status_code == 403)

#AccessError - channel_id refers to a channel that is private and the authorised user is not already a channel member and is not a global owner
def test_channel_join_private(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': False
    })
    user2 = register_a_user2
    resp = requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    })   
    assert(resp.status_code == 403)

#InputError  - channel_id does not refer to a valid channel  
def test_channel_join_invalid_channel(setup, register_a_user1):
    user1 = register_a_user1
    resp = requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user1.text)['token'],
        'channel_id': 666
    })   
    assert(resp.status_code == 400)  

#InputError  - the authorised user is already a member of the channel
def test_channel_join_already_in_channnel(setup, register_a_user1):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    resp = requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user1.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    })   
    assert(resp.status_code == 400)

#success join
def test_channel_join_success(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
    'token': json.loads(user1.text)['token'], 
    'name': 'happy', 
    'is_public': True
    })
    user2 = register_a_user2
    resp = requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    })   
    assert(resp.status_code == 200)

#-------------------channel_invite_v2_test----------------------

#AccessError - the token passed in is invalid
def test_channel_invite_invalid_token(setup):
    resp = requests.post(config.url + 'channel/invite/v2', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
        'channel_id': 5,
        'u_id': 5
    })   
    assert(resp.status_code == 403)

#AccessError - invalid session
def test_channel_invite_invalid_session(setup, register_a_user1):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.post(config.url + 'channel/invite/v2', json={
        'token': json.loads(resp_login.text)['token'], 
        'channel_id': 666,
        'u_id': 666
    })   
    assert(resp.status_code == 403)

#AccessError - channel_id is valid and the authorised user is not a member of the channel
def test_channel_invite_auth_not_in_channel(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    user2 = register_a_user2
    user3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'hello@gmail.com', 
        'password': '1234567', 
        'name_first': 'Yining', 
        'name_last': 'Zhang'
    })
    resp = requests.post(config.url + 'channel/invite/v2', json={
        'token': json.loads(user2.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user3.text)['auth_user_id']
    })   
    assert(resp.status_code == 403)    

#InputError  - channel_id does not refer to a valid channel
def test_channel_invite_invalid_channel(setup, register_a_user1, register_a_user2):
    user2 = register_a_user2
    resp = requests.post(config.url + 'channel/invite/v2', json={
        'token': json.loads(user2.text)['token'], 
        'channel_id': 666,
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    assert(resp.status_code == 400)        

#InputError  - u_id does not refer to a valid user
def test_channel_invite_invalid_u_id(setup, register_a_user1):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    resp = requests.post(config.url + 'channel/invite/v2', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': 666
    })   
    assert(resp.status_code == 400)        

#InputError  - u_id refers to a user who is already a member of the channel
def test_channel_invite_user_already_in_channel(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    user2 = register_a_user2
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    })   
    resp = requests.post(config.url + 'channel/invite/v2', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    assert(resp.status_code == 400)        

#success invite
def test_channel_invite_success(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    user2 = register_a_user2
    resp = requests.post(config.url + 'channel/invite/v2', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    assert(resp.status_code == 200)        

#-------------------channel_leave_v1_test----------------------    

#AccessError - the token passed in is invalid
def test_channel_leave_invalid_token(setup):
    resp = requests.post(config.url + 'channel/leave/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
        'channel_id': 5
    })   
    assert(resp.status_code == 403)

#AccessError - invalid session
def test_channel_leave_invalid_session(setup, register_a_user1):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.post(config.url + 'channel/leave/v1', json={
        'token': json.loads(resp_login.text)['token'], 
        'channel_id': 666
    }) 
    assert(resp.status_code == 403)

#AccessError - channel_id is valid and the authorised user is not a member of the channel
def test_channel_leave_not_member_of_channel(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    user2 = register_a_user2
    resp = requests.post(config.url + 'channel/leave/v1', json={
        'token': json.loads(user2.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id']
    })   
    assert(resp.status_code == 403)    

#InputError - channel_id does not refer to a valid channel
def test_channel_leave_invalid_channel(setup, register_a_user1):
    user1 = register_a_user1
    resp = requests.post(config.url + 'channel/leave/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': 666
    })   
    assert(resp.status_code == 400)  

#leave success
def test_channel_leave_success(setup, register_a_user1):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    resp = requests.post(config.url + 'channel/leave/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id']
    })   
    assert(resp.status_code == 200)  

#leave success2
def test_channel_leave_success2(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    user2 = register_a_user2
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    })   
    resp = requests.post(config.url + 'channel/leave/v1', json={
        'token': json.loads(user2.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id']
    })   
    assert(resp.status_code == 200)  

#-------------------channel_addowner_v1_test----------------------

#AccessError - the token passed in is invalid
def test_channel_addowner_invalid_token(setup):
    resp = requests.post(config.url + 'channel/addowner/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
        'channel_id': 5,
        'u_id': 5
    })   
    assert(resp.status_code == 403)

#AccessError - invalid session
def test_channel_addowner_invalid_session(setup, register_a_user1):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(resp_login.text)['token'], 
        'channel_id': 666,
        'u_id': 666
    })  
    assert(resp.status_code == 403)

def test_global_owner_non_member_cant_addowner_private(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    user2 = register_a_user2
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user2.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    resp = requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    assert(resp.status_code == 403)
    

#AccessError - channel_id is valid and the authorised user does not have owner permissions in the channel
def test_channel_addowner_auth_not_have_permission(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    user2 = register_a_user2
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    }) 
    user3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'hello@gmail.com', 
        'password': '1234567', 
        'name_first': 'Yining', 
        'name_last': 'Zhang'
    })  
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user3.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    })                                                                                 
    resp = requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(user2.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user3.text)['auth_user_id']
    })   
    assert(resp.status_code == 403)

#InputError - channel_id does not refer to a valid channel
def test_channel_addowner_invalid_channel(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    user2 = register_a_user2
    resp = requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': 5,
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    assert(resp.status_code == 400)    

#InputError - u_id is invalid
def test_channel_addowner_invalid_u_id(setup, register_a_user1):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    resp = requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': 6
    })   
    assert(resp.status_code == 400)

#InputError - u_id refers to a user who is not a member of the channel
def test_channel_addowner_u_id_not_in_channel(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    user2 = register_a_user2
    resp = requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    assert(resp.status_code == 400)    

#InputError - u_id refers to a user who is already an owner of the channel
def test_channel_addowner_u_id_already_owner_in_channel(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    user2 = register_a_user2
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    })                                                                              
    requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })
    resp = requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })
    assert(resp.status_code == 400) 

#addowner success
def test_channel_addowner_success(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    user2 = register_a_user2
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    })                                                                              
    resp = requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    assert(resp.status_code == 200)   

#-------------------channel_removeowner_v1_test----------------------

#AccessError - the token passed in is invalid
def test_channel_removeowner_invalid_token(setup):
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
        'channel_id': 5,
        'u_id': 5
    })   
    assert(resp.status_code == 403)    

#AccessError - invalid session
def test_channel_removeowner_invalid_session(setup, register_a_user1):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Yining@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': json.loads(resp_login.text)['token'], 
        'channel_id': 666,
        'u_id': 666
    })   
    assert(resp.status_code == 403)

#AccessError - channel_id is valid and the authorised user does not have owner permissions in the channel
def test_channel_removewner_auth_not_have_permission(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    user2 = register_a_user2
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    }) 
    user3 = requests.post(config.url + 'auth/register/v2', json={
        'email': 'hello@gmail.com', 
        'password': '1234567', 
        'name_first': 'Yining', 
        'name_last': 'Zhang'
    })  
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user3.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    })                                                                                 
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': json.loads(user2.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user3.text)['auth_user_id']
    })   
    assert(resp.status_code == 403)

# InputError - channel_id does not refer to a valid channel
def test_channel_removeowner_invalid_channel(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    user2 = register_a_user2
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': 5,
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    assert(resp.status_code == 400)                            

#InputError - u_id is invalid
def test_channel_removeowner_invalid_u_id(setup, register_a_user1):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': 6
    })   
    assert(resp.status_code == 400)

#InputError - u_id u_id refers to a user who is not an owner of the channel
def test_channel_removeowner_u_id_not_owner_of_channel(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    user2 = register_a_user2
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    }) 
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    assert(resp.status_code == 400)    

#InputError - u_id u_id refers to a user who is currently the only owner of the channel
def test_channel_removeowner_u_id_only_owner_in_channel(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    user2 = register_a_user2
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user2.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    assert(resp.status_code == 400)    

#removeowner success
def test_channel_removeowner_success(setup, register_a_user1, register_a_user2):
    user1 = register_a_user1
    channel = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user1.text)['token'], 
        'name': 'happy', 
        'is_public': True
    })
    user2 = register_a_user2
    requests.post(config.url + 'channel/join/v2', json={
        'token': json.loads(user2.text)['token'],
        'channel_id': json.loads(channel.text)['channel_id']
    })                                                                              
    requests.post(config.url + 'channel/addowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    resp = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': json.loads(user1.text)['token'], 
        'channel_id': json.loads(channel.text)['channel_id'],
        'u_id': json.loads(user2.text)['auth_user_id']
    })   
    assert(resp.status_code == 200)    

#-------------------channel_details_v2_test----------------------
# Test if AccessError occurs when token and channel_id are invalid
def test_channel_details_invalid_token_1(setup):
    resp = requests.get(config.url + 'channel/details/v2', params={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
        'channel_id': 3})   
    assert(resp.status_code == 403)

def test_channel_details_invalid_token_2(setup, register_a_user3):
    user3 = register_a_user3  
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'Libo@gmail.com', 
        'password': '1234567'})
    
    
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']})
    

    resp_deatils = requests.get(config.url + 'channel/details/v2', params={
        'token': json.loads(resp_login.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id']})
    
    assert(resp_deatils.status_code == 403)

# Test if InputError occurs when channel_id is invalid and token is valid 
def test_channel_details_valid_token_and_invalid_channel_id(setup, register_a_user4):
    user4 = register_a_user4
    resp = requests.get(config.url + 'channel/details/v2', params={
        'token': json.loads(user4.text)['token'],
        'channel_id': 1234})
    assert(resp.status_code == 400)

# Test if AccessError occurs when the authorised user is not the member of channel 
def test_channel_details_invalid_user(setup, register_a_user3, register_a_user4):
    user3 = register_a_user3  
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'],
        'name': 'love', 
        'is_public': True })
    user4 = register_a_user4
    resp = requests.get(config.url + 'channel/details/v2', params={
        'token': json.loads(user4.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })
    assert(resp.status_code == 403)   

# Test if provide basic details about the channel.
def test_channel_details_successfully(setup, register_a_user3):
    user3 = register_a_user3
    channel1 = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(user3.text)['token'], 
        'name': 'love', 
        'is_public': True})
    resp = requests.get(config.url + 'channel/details/v2', params={
        'token': json.loads(user3.text)['token'],
        'channel_id': json.loads(channel1.text)['channel_id'] })
    assert json.loads(resp.text) == {'name': 'love', 'is_public': True, 
    'owner_members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'}],
    'all_members': [{'u_id': 1, 'handle_str': 'libocheng', 'email': 'Libo@gmail.com', 'name_first': 'Libo', 'name_last': 'Cheng'}]}

