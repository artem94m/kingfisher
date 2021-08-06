from Crypto.PublicKey import RSA
key = RSA.generate(2048)
f = open('mykey.pem','w')
f.write(key.exportKey(format='PEM'))
f.write(key.exportKey())
f.write(key.export_key(format='PEM'))
f.write(key.export_key())
f.close()