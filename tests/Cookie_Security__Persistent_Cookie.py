def view_method(request):
    res = HttpResponse()
    res.set_cookie("emailCookie", email, max_age=123, secure=True, path='/somethibg', domain="domain.com", httponly=True, samesite=None)
    return res

def view_method(request):
    res = HttpResponse()
    res.set_cookie("emailCookie", email, expires="asdasd", secure=True, path='/somethibg', domain="domain.com", httponly=True)
    return res

def view_method(request):
    res = HttpResponse()
    res.set_cookie("emailCookie", email, expires=None, secure=True, path='/somethibg', domain="domain.com", httponly=True)
    return res