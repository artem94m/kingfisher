def view_method(request):
    res = HttpResponse()
    res.set_cookie("emailCookie", email, path='/somethibg', domain="domain.com", httponly=True, samesite=None)
    return res

def view_method(request):
    res = HttpResponse()
    res.set_cookie("emailCookie", email, secure=False, path='/somethibg', domain="domain.com", httponly=True)
    return res