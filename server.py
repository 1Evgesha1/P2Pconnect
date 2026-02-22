import socket
import threading


clients = []
clients_lock = threading.Lock()
seen_msg = set()
seen_lock = threading.Lock()


def server_msg(msg):
    print(f"[СЕРВЕР] {msg}")


def start_server(server_addr):
    server_sock = socket.socket()
    server_sock.bind(('0.0.0.0', server_addr[1]))
    server_sock.listen()
    server_msg(f"Сервер открыт на {server_addr}")

    while True:
        client_sock, client_addr = server_sock.accept()
        with clients_lock:
            clients.append(client_sock)
        threading.Thread(target=handle_client, args=(client_sock, client_addr), daemon=True).start()


def handle_client(client_sock, client_addr):
    server_msg(f"Подключение: {client_addr}")

    try:
        while True:
            data = client_sock.recv(1024)
            if not data:
                break

            message = data.decode()
            msg_id, msg_txt = message.split('|', 1)

            with seen_lock:
                if msg_id in seen_msg:
                    continue
                seen_msg.add(msg_id)

            with clients_lock:
                clients_copy = clients[:]

            for c in clients_copy:
                if c != client_sock:
                    try:
                        c.sendall(msg_txt.encode())
                    except:
                        with clients_lock:
                            if c in clients:
                                clients.remove(c)
    except Exception as e:
        server_msg(f"Ошибка с {client_addr}: {e}")
    finally:
        server_msg(f"{client_addr} отключился")
        with clients_lock:
            if client_sock in clients:
                clients.remove(client_sock)
        client_sock.close()
