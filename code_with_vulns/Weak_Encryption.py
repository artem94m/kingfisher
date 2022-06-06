from Crypto.Cipher import ARC4, CAST, DES, ARC2, Blowfish



cipher = ARC4.new(tempkey)

cipher = DES.new(key, DES.MODE_OFB)

cipher = ARC2.new(key, ARC2.MODE_CFB, iv)

cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv)

cipher = CAST.new(key, CAST.MODE_OPENPGP, iv)

cipher = DES.new(key, DES.MODE_CTR, counter=ctr)