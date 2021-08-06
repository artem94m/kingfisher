import hashlib, binascii
from django.utils.crypto import pbkdf2

def register(request):
    password = request.GET['password']
    username = request.GET['username']
    dk = pbkdf2(password, None, 100000)
    hash = binascii.hexlify(dk)
    store(username, hash)

hashlib.pbkdf2_hmac(param1, param2, None)