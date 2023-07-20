import pytest
import requests
import json
from src import config

import random



@pytest.fixture
def setup():
    requests.delete(config.url + 'clear/v1')

@pytest.fixture
def register_a_user():
    return requests.post(config.url + 'auth/register/v2',json={
        'email': 'erika@gmail.com', 
        'password': '1234567', 
        'name_first': 'erika', 
        'name_last': 'fu'
    })

@pytest.fixture
def register_a_user1():
    return requests.post(config.url + 'auth/register/v2',json={
        'email': 'clb947156059@gmail.com', 
        'password': '12345678', 
        'name_first': 'Libo', 
        'name_last': 'Cheng'
    })



#-----------------auth_auth_register_v2------------------------
def test_register_v2_invalid_email(setup):
    resp = requests.post(config.url + 'auth/register/v2',json={
        'email': 'invalid email', 
        'password': '1234567', 
        'name_first': 'erika', 
        'name_last': 'fu'
    })
    assert(resp.status_code == 400)

def test_register_v2_existed_email(setup, register_a_user):
    resp = requests.post(config.url + 'auth/register/v2',json={
        'email': 'erika@gmail.com', 
        'password': '1234567', 
        'name_first': 'erika', 
        'name_last': 'fu'
    })

    assert(resp.status_code == 400)

def test_register_v2_password_too_short(setup):
    resp = requests.post(config.url + 'auth/register/v2',json={
        'email': 'jie@gmail.com', 
        'password': '1', 
        'name_first': 'erika', 
        'name_last': 'fu'
    })
    assert(resp.status_code == 400)

def test_register_v2_name_first_wrong_length(setup):
    resp = requests.post(config.url + 'auth/register/v2',json={
        'email': 'erika@gmail.com', 
        'password': '1234567', 
        'name_first': 'erika'*100, 
        'name_last': 'fu'
    })
    assert(resp.status_code == 400)

def test_register_v2_name_last_wrong_length(setup):
    resp = requests.post(config.url + 'auth/register/v2',json={
        'email': 'erika@gmail.com', 
        'password': '1234567', 
        'name_first': 'erika', 
        'name_last': 'fu'*100
    })

    assert(resp.status_code == 400)


def test_register_v2_successful(register_a_user):
    resp = requests.post(config.url + 'auth/register/v2',json={
        'email': 'w17a@gmail.com', 
        'password': '1234567', 
        'name_first': 'erika', 
        'name_last': 'fu'
    })
    assert(resp.status_code == 200)
    assert json.loads(resp.text)['auth_user_id'] == 2

#-----------------auth_login_v2------------------------
def test_login_v2_mismatched_email_1(setup, register_a_user):
    resp = requests.post(config.url + 'auth/login/v2',json={
        'email': 'mismatched_email', 
        'password': '1234567'
    })
    assert(resp.status_code == 400)

def test_login_v2_mismatched_email_2(setup):
    resp = requests.post(config.url + 'auth/login/v2',json={
        'email': 'not_registed@gmail.com', 
        'password': '1234567'
    })
    assert(resp.status_code == 400)

def test_login_v2_incorrect_password(setup, register_a_user):
    resp = requests.post(config.url + 'auth/login/v2',json={
        'email': 'erika@gmail.com',
        'password': 'incorrect_password'
    })
    assert(resp.status_code == 400)


def test_login_v2_successful(setup, register_a_user):
    resp = requests.post(config.url + 'auth/login/v2',json={
        'email': 'erika@gmail.com',
        'password': '1234567'
    })
    assert json.loads(resp.text)['auth_user_id'] == 1

#-------------------auth_logout_v1----------------------
def test_logout_v1_invalid_token_1(setup,register_a_user):
    resp_login = requests.post(config.url + 'auth/login/v2',json={
        'email': 'erika@gmail.com', 
        'password': '1234567'
    })
    
    resp_logout = requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })

    resp_logout = requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    
    assert(resp_logout.status_code == 403)


def test_logout_v1_invalid_token_2(setup):
    resp_logout = requests.post(config.url + 'auth/logout/v1', json={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU'
    })    
    assert(resp_logout.status_code == 403)

#-------------------auth_passwordreset_request_v1_test----------------------
def test_passwordreset_request_v1_invalid_email(setup, register_a_user1):
    resp = requests.post(config.url + 'auth/passwordreset/request/v1',json={
        'email': 'Lin123@gmail.com'
    })

    assert(resp.status_code == 200)




#-------------------auth_passwordreset_reset_v1_test----------------------
def test_passwordreset_reset_v1_invalid_reset_code(setup):
    resp = requests.post(config.url + 'auth/passwordreset/reset/v1',json={
        'reset_code': 'kmjh',
        'new_password': '123456789'
    })

    assert(resp.status_code == 400)


def test_passwordreset_reset_v1_invalid_password(setup, register_a_user1):
    reset_code = str(1289)
    requests.post(config.url + 'auth/passwordreset/request/v1',json={
        'email': 'clb947156059@gmail.com'
    })

    resp = requests.post(config.url + 'auth/passwordreset/reset/v1',json={
        'reset_code': reset_code,
        'new_password': '1234'
    })

    assert(resp.status_code == 400)

def test_passwordreset_reset_v1_successful(setup, register_a_user, register_a_user1):
    reset_code = str(1289)
    requests.post(config.url + 'auth/passwordreset/request/v1',json={
        'email': 'clb947156059@gmail.com'
    })

    resp = requests.post(config.url + 'auth/passwordreset/reset/v1',json={
        'reset_code': reset_code,
        'new_password': '123456789'
    })

    assert(resp.status_code == 200)



