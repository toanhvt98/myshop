from rest_framework.views import APIView
from .config import SimpleJWTConfig,SiteConfig
from .authentication import AuthenticationMixin
# Create your views here.

simplejwt_config = SimpleJWTConfig().get_simple_jwt_config()
site_config = SiteConfig().get_site_config()
class BaseMixinView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def initialize_request(self, request, *args, **kwargs):
        return super().initialize_request(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        """
        {
            'name':'cookie name,
            'value':'cookie value'
            'max_age' : 'cookie max age in seconds',
            'httponly' : True or False, # default site_config['COOKIE_HTTP_ONLY']
            'secure' : True or False, # default site_config['COOKIE_SECURE']
            'samesite' : 'strict' or 'lax' or 'none', # default site_config['COOKIE_SAME_SITE']
            'domain' : 'cookie domain', # default site_config['COOKIE_DOMAIN']
            'path' : 'cookie path', # default site_config['COOKIE_PATH']
        }
        """
        if hasattr(request, '_list_cookies') and isinstance(request._list_cookies, list):
            for data in request._list_cookies:
                response.set_cookie(**data)
        if hasattr(request,'_list_key_deleting_cookies') and isinstance(request._list_key_deleting_cookies, list):
            for data in request._list_key_deleting_cookies:
                response.delete_cookie(data)
        if hasattr(request,'_should_clean_auth_cookie') and request._should_clean_auth_cookie is True:
            response.delete_cookie(simplejwt_config['ACCESS_TOKEN_NAME'])
            response.delete_cookie(simplejwt_config['REFRESH_TOKEN_NAME'])
        return super().finalize_response(request, response, *args, **kwargs)

class ProtectedBaseView(BaseMixinView):
    authentication_classes = (AuthenticationMixin,)
    permission_classes = ()

class AuthBaseView(BaseMixinView):
    authentication_classes = ()
    permission_classes = ()
