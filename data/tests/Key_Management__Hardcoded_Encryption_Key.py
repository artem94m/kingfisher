from Crypto.Ciphers import AES
encryption_key = b'_hardcoded__key_'
cipher = AES.new("asdasd", AES.MODE_CFB, iv)
msg = iv + cipher.encrypt(b'Attack at dawn')