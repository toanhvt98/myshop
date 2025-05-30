import json

from django.conf import settings
from cryptography.fernet import Fernet
from .config import SimpleJWTConfig,SiteConfig
simplejwt_config = SimpleJWTConfig().get_simple_jwt_config()
site_config = SiteConfig().get_site_config()
def set_cookies(
        key:str,
        value:str,
        max_age:int,
        httponly=site_config['COOKIE_HTTP_ONLY'],
        secure=site_config['COOKIE_SECURE'],
        samesite=site_config['COOKIE_SAME_SITE'],
        domain=site_config['COOKIE_DOMAIN'],
        path=site_config['COOKIE_PATH']
        )->dict:
   return {
       'key':key,
       'value':value,
       'max_age':max_age,
       'httponly':httponly,
       'secure':secure,
       'samesite':samesite,
       'domain':domain,
       'path':path
   }

def encrypt_data(data:dict,secret_key=settings.FIELD_ENCRYPTION_KEY)->str:
    f = Fernet(secret_key)
    json_data_str = json.dumps(data)
    data_bytes = json_data_str.encode('utf-8')
    return f.encrypt(data_bytes).decode('utf-8')

def decrypt_data(encrypted_data:str,secret_key=settings.FIELD_ENCRYPTION_KEY)->dict:
    f = Fernet(secret_key)
    decrypted_data_json = f.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
    return json.loads(decrypted_data_json)