import hashlib
import json

from cryptography.fernet import Fernet

from base.config import AuthConfig
import random
import string

def convert_seconds_to_minutes(seconds):
    return seconds // 60

def generate_code():
    otp_config = AuthConfig().get_auth_config()
    OTP_MIXED_CASE = otp_config['OTP_MIXED_CASE']
    OTP_LENGTH = otp_config['OTP_LENGTH']
    otp = ''
    if OTP_MIXED_CASE:
        for i in range(OTP_LENGTH):
            otp += random.choice(string.ascii_letters + string.digits)
    else:
        for i in range(OTP_LENGTH):
            otp += str(random.randint(0, 9))
    return otp

def generate_secret_key():
    return Fernet.generate_key().decode('utf-8')

def decrypt_data_secret_key(encrypted_data:str, secret_key:str)->dict:
    fernet = Fernet(secret_key.encode('utf-8'))
    decrypted_data_json = fernet.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
    return json.loads(decrypted_data_json)

def encrypt_data_secret_key(data:dict, secret_key:str)->str:
    fernet = Fernet(secret_key.encode('utf-8'))
    json_data_str = json.dumps(data)
    encrypted_data = fernet.encrypt(json_data_str.encode('utf-8')).decode('utf-8')
    return encrypted_data

def hash_email(email:str):
    normalized_email = email.strip().lower()
    return hashlib.sha256(normalized_email.encode('utf-8')).hexdigest()