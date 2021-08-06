import hmac

mac = hmac.new("", plaintext).hexdigest()

test = hmac.digest("", msg, digest)