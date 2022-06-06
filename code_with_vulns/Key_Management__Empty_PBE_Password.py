from hashlib import pbkdf2_hmac

dk = pbkdf2_hmac('sha256', '', salt, 100000)