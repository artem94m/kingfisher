def view_method(request):
    res = HttpResponse()
    res.set_cookie("emailCookie", email, secure=True, path='/', domain="domain.com", httponly=True, samesite=None)
    return res

def view_method(request):
    res = HttpResponse()
    res.set_cookie("emailCookie", email, secure=True, domain="domain.com", httponly=True)
    return res