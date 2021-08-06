import ssl
ssl_sock = ssl.wrap_socket(s)

ssl_sock = ssl.wrap_socket(s, cert_reqs=CERT_NONE)
ssl_sock = ssl.wrap_socket(s, 2, 3, 4, CERT_OPTIONAL)