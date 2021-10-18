from django.contrib.auth.hashers import make_password
from django.utils.crypto import salted_hmac

my_salt = "salt"

data["sALT"] = "salr"

make_password(param1, param2, salt="asdw")

salted_hmac(param1, "aasdw")