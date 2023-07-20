import pytest
import requests
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