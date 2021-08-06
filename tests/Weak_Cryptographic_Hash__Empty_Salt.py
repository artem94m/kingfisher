from django.contrib.auth.hashers import make_password
from django.utils.crypto import salted_hmac

custom_salt = ""

datap["saLt"] = ""

password = make_password(param1, "")

hmac = salted_hmac(param1, "")