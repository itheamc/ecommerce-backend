from django.contrib.auth.backends import BaseBackend
from authentication.models import ASquareUser


# -------------------------------@mit--------------------------------
# ModelBackends for authenticating ASquareUser
class ASquareUserModelBackend(BaseBackend):

    # Authenticate a user based on email and password
    def authenticate(self, request, email=None, password=None):
        try:
            user = ASquareUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except ASquareUser.DoesNotExist:
            return None

    # Get a user by ID
    def get_user(self, user_id):
        try:
            return ASquareUser.objects.get(pk=user_id)
        except ASquareUser.DoesNotExist:
            return None
