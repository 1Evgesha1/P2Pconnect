import socket
import threading
import sys
import uuid
import time

peers = []
seen_msg = set()
nickname = ""
server_list = []
current_server_index = 0

def send_message():
    while True:
        msg = input()
        msg_id = str(uuid.uuid4())
        full_text = f"{nickname}: {msg}"
        full_msg = f"{msg_id}|{full_text}"

        for peer in peers:
            try:
                peer.send(full_msg.encode())
            except:
                peers.remove(peer)

        seen_msg.add(msg_id)
        print(full_text)

def handle_client(conn, addr):
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break

            message = data.decode()
            msg_id, msg_text = message.split("|", 1)

            if msg_id in seen_msg:
                continue

            seen_msg.add(msg_id)
            print(msg_text)

            for peer in peers:
                if peer != conn:
                    try:
                        peer.send(data)
                    except:
                        peers.remove(peer)
        except:
            break

    if conn in peers:
        peers.remove(conn)
    conn.close()

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen()
    print(f"[Сервер запущен на порту {port}]")

    while True:
        conn, addr = server.accept()
        peers.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def connect_to_next_server(start_index=0):
    global current_server_index
    for i in range(start_index, len(server_list)):
        ip, port = server_list[i]
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip, port))
            peers.append(client)
            threading.Thread(target=handle_client, args=(client, (ip, port)), daemon=True).start()
            print(f"[+] Подключен к серверу {ip}:{port}")
            current_server_index = i
            return i
        except:
            continue
    print("[-] Нет доступных серверов")
    return None

def monitor_connection():
    global current_server_index
    while True:
        alive = False
        for peer in peers:
            try:
                peer.send(b"ping")
                alive = True
                break
            except:
                if peer in peers:
                    peers.remove(peer)
        if not alive:
            print("[!] Основной сервер недоступен, переподключаемся к следующему...")

            if current_server_index is None:
                current_server_index=0
            else:
                current_server_index+=1

            current_server_index=connect_to_next_server(current_server_index)
        time.sleep(5)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование:")
        print("python p2pApp.py <порт_этого_пира> <ip1:port1> <ip2:port2>")
        sys.exit(1)

    nickname = input("Введите ваш никнейм: ")
    local_port = int(sys.argv[1])

    for s in sys.argv[2:]:
        ip, port = s.split(":")
        server_list.append((ip, int(port)))

    threading.Thread(target=start_server, args=(local_port,), daemon=True).start()

    connect_to_next_server(0)

    threading.Thread(target=monitor_connection, daemon=True).start()

    send_message()