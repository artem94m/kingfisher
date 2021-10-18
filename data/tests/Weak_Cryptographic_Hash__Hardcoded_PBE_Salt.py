import hashlib
from django.utils.crypto import pbkdf2

hashlib.pbkdf2_hmac(param1, param2, "salt")

pbkdf2(param1, "salt")