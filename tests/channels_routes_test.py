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
        'email': 'libo@gmail.com', 
        'password': '1234567', 
        'name_first': 'libo', 
        'name_last': 'cheng'})

#-------------------channels_create_v2_test----------------------

def test_channels_create_invalid_token(setup):
    resp = requests.post(config.url + 'channels/create/v2',
                         json={'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                                        'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU', 
                               'name': 'administration', 
                               'is_public': True})
    assert(resp.status_code == 403)

def test_channels_create_invalid_session_id(setup, register_a_user):
    resp_login = requests.post(config.url + 'auth/login/v2',json={
        'email': 'libo@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(resp_login.text)['token'], 
        'name': '',
        'is_public': True})
    assert(resp.status_code == 403)

def test_channels_create_invalid_channel_name_1(setup, register_a_user):
    resp_user = register_a_user
    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(resp_user.text)['token'], 
        'name': '',
        'is_public': True})
    assert(resp.status_code == 400)

def test_channels_create_invalid_channel_name_2(setup, register_a_user):
    resp_user = register_a_user
    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(resp_user.text)['token'], 
        'name': 'thisnameismorethan20characters', 
        'is_public': True})
    assert(resp.status_code == 400) 

def test_channnels_create_successfully_1(setup, register_a_user):
    resp_user = register_a_user
    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(resp_user.text)['token'], 
        'name': 'administration', 
        'is_public': True})
    assert json.loads(resp.text)['channel_id'] == 1

#-------------------channels_list_v2_test----------------------

def test_channels_list_invalid_token(setup):
    resp = requests.get(config.url + 'channels/list/v2', params={'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                                                                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU'})
    assert(resp.status_code == 403)

def test_channels_list_invalid_session_id(setup, register_a_user):
    resp_login = requests.post(config.url + 'auth/login/v2',json={
        'email': 'libo@gmail.com', 
        'password': '1234567'
    })
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })
    resp = requests.get(config.url + 'channels/list/v2', params={'token': json.loads(resp_login.text)['token']})
    assert(resp.status_code == 403)

def test_channels_list_empty(setup, register_a_user):
    resp_user = register_a_user
    resp = requests.get(config.url + 'channels/list/v2', params={'token': json.loads(resp_user.text)['token']})
    assert json.loads(resp.text)['channels'] == []


def test_channels_list_successful(setup, register_a_user):
    resp_user = register_a_user
    resp = requests.post(config.url + 'channels/create/v2',
                        json={'token': json.loads(resp_user.text)['token'], 
                            'name': 'administration', 
                            'is_public': True})
    resp = requests.get(config.url + 'channels/list/v2', params={'token': json.loads(resp_user.text)['token']})
    assert json.loads(resp.text) == {'channels': [{'channel_id': 1, 'name': 'administration'}]}

def test_channels_list_successful_2(setup, register_a_user):
    resp_user = register_a_user
    requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(resp_user.text)['token'],
        'name': 'administration', 
        'is_public': True})
    resp = requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(resp_user.text)['token'], 
        'name': 'staff', 
        'is_public': False})
    resp = requests.get(config.url + 'channels/list/v2', params={'token': json.loads(resp_user.text)['token']})   
    assert json.loads(resp.text) == {'channels': [{'channel_id': 1, 'name': 'administration'},{'channel_id': 2, 'name': 'staff'}]}

#-------------------channels_listall_v2_test----------------------
def test_channels_listall_invalid_token_1(setup):
    resp = requests.get(config.url + 'channels/listall/v2', params={
        'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjoxLCJzZXNzaW9uX2lkIjoiMjNlZDNjZD'\
                 'ItMzA5OS0xMWVjLWI1YjMtMDA1MDU2OTEzOTU4In0.9HDFUTmmoXtS5PQDUDJ6S36MTGRKxdiRlMAv06NmmJU'})
    assert(resp.status_code == 403)

def test_channel_listall_invalid_token_2(setup, register_a_user):
    resp_login = requests.post(config.url + 'auth/login/v2', json={
        'email': 'libo@gmail.com', 
        'password': '1234567'})
    
    requests.post(config.url + 'auth/logout/v1', json={
        'token': json.loads(resp_login.text)['token']
    })

    resp_listall = requests.get(config.url + 'channels/listall/v2', params={
        'token': json.loads(resp_login.text)['token'] })
    
    assert(resp_listall.status_code == 403)

def test_channels_listall_empty(setup, register_a_user):
    resp_user = register_a_user
    resp = requests.get(config.url + 'channels/listall/v2', params={
        'token': json.loads(resp_user.text)['token']})
    assert json.loads(resp.text)['channels'] == []


def test_channels_listall_successful(setup, register_a_user):
    resp_user = register_a_user
    requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(resp_user.text)['token'], 
        'name': 'love', 
        'is_public': True})
    resp = requests.get(config.url + 'channels/listall/v2', params={
        'token': json.loads(resp_user.text)['token']})
    assert json.loads(resp.text) == {'channels': [{'channel_id': 1, 'name': 'love'}]}

def test_channels_listall_successful_2(setup, register_a_user):
    resp_user = register_a_user
    requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(resp_user.text)['token'], 
        'name': 'love', 
        'is_public': True})
    requests.post(config.url + 'channels/create/v2', json={
        'token': json.loads(resp_user.text)['token'], 
        'name': 'staff', 
        'is_public': False})

    resp = requests.get(config.url + 'channels/listall/v2', params={
        'token': json.loads(resp_user.text)['token']})
    assert json.loads(resp.text) == {'channels': [{'channel_id': 1, 'name': 'love'}, {'channel_id': 2, 'name': 'staff'}]}


