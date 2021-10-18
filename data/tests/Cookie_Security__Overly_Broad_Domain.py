
def view_method(request):
    res = HttpResponse()
    res.set_cookie("emailCookie", email, secure=True, path='/somethibg', domain=".domain.com", httponly=True)
    return res