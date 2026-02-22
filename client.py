import socket
import threading
import uuid;
import sys



def receive_messages(client_sock):
    while True:
        try:
            data = client_sock.recv(1024)
            if not data:
                break
            print(f"\n{data.decode()}")
            print('> ', end='', flush=True) 
        except:
            break

def send_message(client_sock):
    nickname = input("Your name: ")

    while True:
        msg = input("> ")

        if msg.lower() == "!quit":
            break

        msg_id = str(uuid.uuid4())
        full_text = f"{nickname}: {msg}"
        full_msg = f"{msg_id}|{full_text}"

        client_sock.sendall(full_msg.encode())
    
    client_sock.close()


def connect_to_server(server_addr):
    client_sock = socket.socket()
    client_sock.connect(server_addr)

    threading.Thread(target=receive_messages, args=(client_sock,), daemon=True).start()

    send_message(client_sock)
