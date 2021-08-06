from django.contrib.auth.hashers import make_password
from django.utils.crypto import salted_hmac

salt = None

data = {"my_salt": None}

make_password(param1, None)
salted_hmac(param1, param2, salt=None)