import socket
import threading
import sys
import uuid

peers = []
seen_msg=set()


def send_mesage():
    while True:
        msg=input()
        msg_id=str(uuid.uuid4())
        full_text= f"{nickname}:{msg}"
        full_msg=f"{msg_id}|{full_text}"

        for peer in peers:
            try:
                peer.send(full_msg.encode())
            except:
                pass

        seen_msg.add(msg_id)

def handle_client(conn,addr):

    print(f"[+] Подключен пир {addr}")
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break

            message=data.decode()
            msg_id,msg_text=message.split("|", 1)

            if msg_id in seen_msg:
                continue

            seen_msg.add(msg_id)
            print(msg_text)

            for peer in peers:
                if peer != conn:
                    try:
                        peer.send(data)
                    except:
                        pass
        except:
            break

    print(f"[-] Пир {addr} отключился")

    if conn in peers:
        peers.remove(conn)

    conn.close()

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen()

    print(f"Server is on, on this port ->{port}")

    while True:
        conn, addr = server.accept()
        peers.append(conn)

        threading.Thread(target=handle_client, args=(conn,addr), daemon=True).start()

def connect_to_peer(ip,port):
    client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip,port))
    peers.append(client)

    threading.Thread(target=handle_client, args=(client,(ip,port)), daemon=True).start()

if __name__=="__main__":
    if len(sys.argv)<2:
        print("Using:")
        print("python p2pApp.py <port> [peer_ip] [peer_port]")
        sys.exit(1)

    nickname = input("Enter your nickname-> ")
    port = int(sys.argv[1])

    threading.Thread(target=start_server, args=(port,), daemon=True).start()

    if len(sys.argv)==4:
        peer_ip=sys.argv[2]
        peer_port=int(sys.argv[3])
        connect_to_peer(peer_ip,peer_port)

    threading.Thread(target=send_mesage,daemon=True).start()

    while True:
        pass
