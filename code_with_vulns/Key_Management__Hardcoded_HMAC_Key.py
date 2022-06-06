import hmac

mac = hmac.new("secret", plaintext).hexdigest()

test = hmac.digest("secret", param2, param3)