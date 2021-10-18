import hashlib

from Crypto.Hash import MD4, MD5, RIPEMD, SHA

hashed = hashlib.md4(something)
hashed = hashlib.md5(something)
hashed = hashlib.sha1(something)
hashed = hashlib.ripemd160(something)

h = MD4.new()
h = MD5.new()
h = RIPEMD.new()
h = SHA.new()

from cryptography.hazmat.primitives import hashes
digest = hashes.Hash(hashes.MD5())
digest = hashes.Hash(hashes.SHA1())