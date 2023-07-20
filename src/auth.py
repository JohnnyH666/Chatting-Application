from datetime import datetime 
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from src.data_store import data_store
from src.error import InputError, AccessError
from src.helper_functions import generateToken, getUserFromToken, getSessionFromToken, generateSessionId, search_session,search_user, search_user_by_email, in_removed_list

import re
VALIDEMAIL = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def hash(string):
    return hashlib.sha256(string.encode()).hexdigest()


def auth_login_v2(email, password):
    '''
    Given a registered user's email and password, returns their `token` value.

    Arguments:
        email (string)    - A registered email address, which should be a valid format
        password (string) - The password corresponding to the registered email   

    Exceptions:
        InputError - Occurs when email entered does not belong to a user
        InputError - Occurs when password is not correct

    Return Value:
        Returns 'token' and 'auth_user_id' when user was logged in successfully

    '''
    store = data_store.get()
    registered_user = False

    if not (re.fullmatch(VALIDEMAIL, email)):
        raise InputError(description="Invalid format of email")
    
    # search email in database
    for user in store['users']:
        if user['email'] == email:
            registered_user = True
            target_user = user
            break
   
    if not registered_user:
        raise InputError(description="Email entered does not belong to a user")
    
    if target_user['password'] != hash(password):
        raise InputError(description="Password is incorrect")
        
    session_id = generateSessionId()
    for user in store['users']:
        if user == target_user:
            user['session_list'].append(session_id)

    data_store.set(store)

    return {
        'token': generateToken(target_user['u_id'], session_id),
        'auth_user_id': target_user['u_id'],
    }


def auth_register_v2(email, password, name_first, name_last):
    '''
    Given a user's first and last name, email address, and password, create a new account for 
    them and return a new `token`. A handle is generated that is the concatenation of their 
    casted-to-lowercase alphanumeric (a-z0-9) first name and last name (i.e. make lowercase then
    remove non-alphanumeric characters). If the concatenation is longer than 20 characters, it is 
    cut off at 20 characters. Once you've concatenated it, if the handle is once again taken, append 
    the concatenated names with the smallest number (starting from 0) that forms a new handle that 
    isn't already taken. 

    Arguments:
        email (string)      - A valid email address
        password (string)   - A string which cannot be empty
        name_first (string) - The frist name of the user which must contain alphanumeric (a-z0-9) character
        name_last (string)  - The last name of the user which must contain alphanumeric (a-z0-9) character

    Exceptions:
        InputError - email entered is not a valid email 
        InputError - email address is already being used by another user
        InputError - length of password is less than 6 characters
        InputError - length of name_first is not between 1 and 50 characters inclusive
        InputError - length of name_last is not between 1 and 50 characters inclusive

    Return Value:
        Returns 'auth_user_id' and 'token' when user registered successfully

    '''
    store = data_store.get()

    # Some cases that will report errors:
    if not (re.fullmatch(VALIDEMAIL, email)):
        raise InputError(description="Invalid format of email")
    
    if any(user['email'] == email for user in store['users']):
        raise InputError(description="Email address is already being used")

    if len(password) < 6:
        raise InputError(description="Password is less than 6 characters")
    
    if len(name_first) not in range(1, 51):
        raise InputError(description="The length of name_first is not between 1 and 50")

    if len(name_last) not in range(1, 51):
        raise InputError(description="The length of name_last is not between 1 and 50")

    # auth_user_id start from 1
    new_id = len(store['users']) + 1  
    session_id = generateSessionId()
    token = generateToken(new_id, session_id)
    
    handle = (name_first + name_last).lower()
    # remove non-alphanumeric characters
    handle = re.sub(r'[^a-zA-Z0-9]', '', handle)
    # If the concatenation exceeds 20 characters, 
    # it is cut off at 20 characters.
    handle = handle[:20]
    # if the handle is once again taken, append the concatenated names with the 
    # smallest number (starting from 0) that forms a new handle that isn't already taken. 
    final_num = 0
    handle_len = len(handle)
    for user in store['users']:
        if user['handle_str'] == handle:
            handle = handle[: handle_len] + str(final_num)
            final_num += 1
    
    # if the user is a member, the permission_id is 2
    permission_id = 2
    # if the user is a owner, the permission_id is 1 
    # (owner is the very first user who signs up)
    if new_id == 1:
        permission_id = 1
    store['users'].append({'email': email, 
                           'password': hash(password), 
                           'name_first': name_first, 
                           'name_last': name_last,
                           'u_id': new_id,  
                           'handle_str': handle,
                           'permission_id': permission_id,
                           'session_list':[session_id],
                           'channels_joined': [{'num_channels_joined': 0, 'time_stamp': int(datetime.timestamp(datetime.now()))}],
                           'dms_joined': [{'num_dms_joined': 0, 'time_stamp': int(datetime.timestamp(datetime.now()))}],
                           'messages_sent': [{'num_messages_sent': 0, 'time_stamp': int(datetime.timestamp(datetime.now()))}],
                           'involvement_rate': 0,
                           'profile_img_url': '',
                           'reset_code_list': []
                          })
    # update workspace stats
    store['workspace_stats']['channels_exist'].append({'num_channels_exist': 0, 'time_stamp': int(datetime.timestamp(datetime.now()))})
    store['workspace_stats']['dms_exist'].append({'num_dms_exist': 0, 'time_stamp': int(datetime.timestamp(datetime.now()))})
    store['workspace_stats']['messages_exist'].append({'num_messages_exist': 0, 'time_stamp': int(datetime.timestamp(datetime.now()))})
    data_store.set(store)
    return {
        'token': token,
        'auth_user_id': new_id,
    }

def auth_logout_v1(token):
    '''
    Given an active token, invalidates the token to log the user out.

    Arguments:
        token (string) - determine the user ID 
    
    Exceptions:
        AccessError - the token passed in is invalid

    Return Value:
        Returns { } when user logout successfully

    '''
    store = data_store.get()
    u_id = getUserFromToken(token)
    user = search_user('u_id', u_id)
    if user is None:
        raise AccessError(description="the token passed in is invalid")

    session_id = getSessionFromToken(token)
    session = search_session(session_id, u_id)
    if (session is None) or (in_removed_list(user)):
        raise AccessError(description="the token passed in is invalid")
    
    # find out the user from the database, then delete his token
    index = int(u_id) - 1
    store['users'][index]['session_list'].remove(session_id)
    return { }


def auth_passwordreset_request_v1(email):
    '''
    Given an email address, if the user is a registered user, sends them an email containing a specific secret code

    Arguments:
        email (string) - send the specific secret code to the email
    
    Exceptions: N/A

    Return Value:
        Returns { } 

    '''
    store = data_store.get()
    # send email and build reset_code
    user = search_user_by_email('email', email)
    if user != None:
        mail_host = 'smtp.qq.com'
        mail_user = '947156059@qq.com'
        mail_pass = 'ewrezegcuopmbdjd'
        sender = '947156059@qq.com'
        receiver = email
        reset_code = str(1289)
        dic = {'reset_code': reset_code, 'valid': True}
        user['reset_code_list'].append(dic)
        message = MIMEText(reset_code, 'plain', 'utf-8')
        message['From'] = Header('Andy', 'utf-8')
        message['To'] = Header('to:user', 'utf-8')
        subject = 'This is a specific secret code(reset_code)'
        message['subject'] = Header(subject, 'utf-8')

        smtpObj = smtplib.SMTP(mail_host)
        smtpObj.connect(mail_host, 25)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receiver, message.as_string())
        smtpObj.quit()
           
        # logout all session 
        user['session_list'].clear()


    data_store.set(store)
    return {}


def auth_passwordreset_reset_v1(reset_code, new_password):
    '''
    Given a reset code for a user, set that user's new password to the password provided.

    Arguments:
        reset_code (string) - determine the user ID 
        new_password (string) - new password
    
    Exceptions:
        InputError - the reset_code is invalid
        InputError - password entered is less than 6 characters long

    Return Value:
        Returns { } 

    '''
    store = data_store.get()
    # length of password < 6 
    if len(new_password) < 6:
        raise InputError(description="the new_password is less than 6 characters long")

    # change password
    for user in store['users']:
        for dictionary in user['reset_code_list']:
            if dictionary == {'reset_code': reset_code, 'valid': True}:
                user['password'] = hash(new_password)
                dictionary = [{'reset_code': reset_code, 'valid': False}]
                data_store.set(store)        
                return {}         
    # invalid reset_code
    raise InputError(description="the reset_code passed in is invalid")
