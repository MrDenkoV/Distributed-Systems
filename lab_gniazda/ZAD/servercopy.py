import socket
import threading
import select


server_ip = '127.0.0.1'
server_port = 9009
server_address = (server_ip, server_port)

buff_size = 1024


def listen(conn, addr, conns):
    conn.sendto("Welcome!".encode(), addr)

    while True:
        try:
            data = conn.recv(buff_size)
            if not data:
                conns[:] = list(filter(lambda x: x != (conn, addr), conns))
                print(len(conns), "active users")
                conn.shutdown()
                conn.close()
                exit()
            
            for reciver in list(filter(lambda x: x!=(conn, addr), conns)):
                try:
                    reciver[0].send(data)
                except:
                    reciver[0].close()
                    conns[:] = list(filter(lambda x: x!=reciver, conns))
            print(data.decode())
        except:
            return


def listen_broad(broad, conns):
    while True:
        try:
            data = broad.recvfrom(buff_size)

            for receiver in list(filter(lambda x: x[1] != data[1], conns)):
                broad.sendto(data[0], receiver[1])
            data = data[0]
            print(data.decode())
        except:
             return


if __name__ == "__main__":
    print("Chat server\nCtrl+c to quit\n")
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(server_address)

        broad_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        broad_server.bind(server_address)

        conns = []
        threads = [threading.Thread(target=listen_broad, args=(broad_server, conns,), daemon=True)]
        threads[-1].start()
        while True:
            server.listen()
            conn, addr = server.accept()
            conns += [(conn, addr)]
            threads += [threading.Thread(target=listen, args=(conn, addr, conns,), daemon=True)]
            threads[-1].start()
            print(len(conns), "active users")
    except KeyboardInterrupt:
        print("Closing")
    finally:
        for conn in conns:
            if conn:
                conn[0].close()
        if server:
            # server.shutdown(socket.SHUT_RDWR)
            server.close()
        if broad_server:
            broad_server.close()