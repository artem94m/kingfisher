import ssl

ssl.wrap_socket(sock, keyfile=None, certfile=None, server_side=False, cert_reqs=CERT_REQUIRED, ssl_version=ssl.PROTOCOL_SSLv23, ca_certs=None, do_handshake_on_connect=True, suppress_ragged_eofs=True, ciphers=None)

ssl.wrap_socket(sock, keyfile=None, certfile=None, server_side=False, cert_reqs=CERT_REQUIRED, ssl_version=ssl.PROTOCOL_SSLv2, ca_certs=None, do_handshake_on_connect=True, suppress_ragged_eofs=True, ciphers=None)

ssl.wrap_socket(sock, keyfile=None, certfile=None, server_side=False, cert_reqs=CERT_REQUIRED, ssl_version=ssl.PROTOCOL_SSLv3, ca_certs=None, do_handshake_on_connect=True, suppress_ragged_eofs=True, ciphers=None)