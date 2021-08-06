from Crypto.Cipher import AES, CAST, DES3, ARC2, DES, Blowfish

cipher = AES.new(key, AES.MODE_CTR, iv, counter)

cipher = DES3.new(key, DES3.MODE_CTR, random_iv)

cipher = ARC2.new(key, ARC2.MODE_CTR, random_iv)

cipher = DES.new(key, DES.MODE_CTR, random_iv)

cipher = Blowfish.new(key, Blowfish.MODE_CTR, random_iv)

cipher = CAST.new(key, CAST.MODE_CTR, random_iv)