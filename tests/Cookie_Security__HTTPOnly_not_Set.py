def view_method(request):
    res = HttpResponse()
    res.set_cookie("emailCookie", email, secure=True, path='/somethibg', domain="domain.com", samesite=None)
    return res

def view_method(request):
    res = HttpResponse()
    res.set_cookie("emailCookie", email, secure=True, path='/somethibg', domain="domain.com", httponly=False)
    return res