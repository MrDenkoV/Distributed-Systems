import socket
import sys
import threading
import select
import struct


server_ip = '127.0.0.1'
server_port = 9009
server_address = (server_ip, server_port)

multi_ip = '224.51.105.104'
multi_port = 9006
multi_address = (multi_ip, multi_port)

buff_size = 1024


def listen(client, broad_client, multi_client, nick):
    while True:
        try:
            socks,_,_ = select.select([client, broad_client, multi_client], [],[])
            data = None
            if client in socks:
                data = client.recv(buff_size)
                if not data:
                    print("Disconected")
                    client.shutdown(socket.SHUT_RDWR)
                    return

            if broad_client in socks:
                data,_ = broad_client.recvfrom(buff_size)
            if multi_client in socks:
                data,_ = multi_client.recvfrom(buff_size)

            print("\r"+data.decode())
            print(f"\r{nick}: ", end="")
        except Exception:
            exit()


if __name__ == '__main__':
    print('Chat Client\nCtrl+c to quit\n:u for udp broadcast or :m for multicast\n')
    nick = input("ENTER NICKNAME:")
    print(f"Hi {nick}, setting up connection")
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        client.connect(server_address)
        
        broad_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        broad_client.bind(('', client.getsockname()[1]))
        
        multi_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        multi_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        multi_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        multi_client.bind(('', multi_port))
        mreq = struct.pack('4sl', socket.inet_aton(multi_ip), socket.INADDR_ANY)
        multi_client.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        print(f"connected to {server_ip}:{server_port}")
        listener = threading.Thread(target=listen, args=(client,broad_client,multi_client,nick,), daemon=True)
        listener.start()
        while True:
            txt = input("\r"+nick+": ")
            if not listener.is_alive():
                raise ConnectionRefusedError
            if txt and txt[0:2].lower() == ':u':
                broad_client.sendto((nick+': '+txt[2:]).encode(), server_address)
            elif txt and txt[0:2].lower() == ':m':
                multi_client.sendto((nick+': '+txt[2:]).encode(), multi_address)
            else:
                client.sendall((nick+': '+txt).encode())
            
    except KeyboardInterrupt:
        print("Disconnecting")
    except ConnectionRefusedError:
        print("No server connection")
    finally:
        if client:
            # client.shutdown(socket.SHUT_RDWR)
            client.close()
        if broad_client:
            broad_client.close()
        if multi_client:
            multi_client.close()
        


