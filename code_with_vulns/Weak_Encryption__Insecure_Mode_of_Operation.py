from Crypto.Cipher import AES, DES3, ARC2, DES, Blowfish

cipher = AES.new(key, AES.MODE_ECB, random_iv)
cipher = AES.new(key, AES.MODE_CBC, random_iv)

cipher = DES3.new(key, DES3.MODE_ECB, random_iv)
cipher = DES3.new(key, DES3.MODE_CBC, random_iv)

cipher = ARC2.new(key, ARC2.MODE_ECB, random_iv)
cipher = ARC2.new(key, ARC2.MODE_CBC, random_iv)

cipher = DES.new(key, DES.MODE_ECB, random_iv)
cipher = DES.new(key, DES.MODE_CBC, random_iv)

cipher = Blowfish.new(key, Blowfish.MODE_ECB, random_iv)
cipher = Blowfish.new(key, Blowfish.MODE_CBC, random_iv)

cipher = CAST.new(key, CAST.MODE_ECB, random_iv)
cipher = CAST.new(key, CAST.MODE_CBC, random_iv)