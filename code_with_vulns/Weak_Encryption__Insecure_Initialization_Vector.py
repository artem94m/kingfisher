from Crypto.Ciphers import AES

cipher = AES.new(key, AES.MODE_CFB, iv="as323")

cipher = AES.new(key, AES.MODE_CFB, IV=123)

iv = r"bsadasd"
IV = b"asda2123"
init_vector = 123123123