from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
UserModel = get_user_model()
class CustomBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return True