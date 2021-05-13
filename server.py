import socket
import threading
import ssl

HOST_NAME = '127.0.0.1'
BIND_PORT = 8080
MAX_REQUEST_LEN = 2 ** 20
MAX_CONN = 256


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST_NAME, BIND_PORT))
        server_socket.listen(MAX_CONN)

        while True:
            client_socket, client_address = server_socket.accept()
            data = client_socket.recv(MAX_REQUEST_LEN)
            # conn_string(client_socket, data, client_address)
            threading.Thread(target=conn_string, args=(client_socket, data, client_address)).start()
            print(threading.active_count())


def conn_string(client_socket, data, client_address):
    try:
        data = data.decode()
        first_line = data.splitlines()[0]
        url = first_line.split()[1]
        method = first_line.split()[0]
    except IndexError:
        return
    print(method)
    is_http = method == 'CONNECT'

    http_pos = url.find("://")
    if http_pos == -1:
        temp = url
    else:
        temp = url[http_pos + 3:]
    port_pos = temp.find(":")
    web_server_pos = temp.find("/")
    if port_pos == -1:
        port = 80
        web_server = temp[:web_server_pos]
    else:
        port = int(temp[port_pos + 1:])
        web_server = temp[:port_pos]

    print("New connection:", web_server, port)

    proxy_server(web_server, port, client_socket, data, client_address, is_http)


def proxy_server(web_server, port, client_socket, data, client_address, is_https):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((web_server, port))
        if is_https:
            sock = ssl.wrap_socket(sock, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE,
                                   ssl_version=ssl.PROTOCOL_SSLv23)
        sock.send(data.encode())
        try:
            while True:
                reply = sock.recv(MAX_REQUEST_LEN)
                if len(reply) > 0:

                    print(reply)
                    client_socket.send(reply)

                else:
                    print("empty break")
                    break
        except ConnectionAbortedError as e:
            print("send exc", e)
        except ConnectionResetError as e:
            print(e)

    client_socket.close()


if __name__ == '__main__':
    main()
