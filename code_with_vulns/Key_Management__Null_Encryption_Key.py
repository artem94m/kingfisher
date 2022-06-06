from Crypto.Ciphers import AES
cipher = AES.new(None, AES.MODE_CFB, iv)
msg = iv + cipher.encrypt(b'Attack at dawn')

my_key = None