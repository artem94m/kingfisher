from hashlib import pbkdf2_hmac

dk = pbkdf2_hmac('sha256', 'password', salt, 100000)
