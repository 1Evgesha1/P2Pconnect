import socket
import threading
from server import *
from client import *



#---PROGRAM START---
if __name__ == "__main__":
    server_ip = input("Айпишник (тот что в радмине): ")
    server_port = int(input("Порт: "))
    server_addr = (server_ip, server_port)

    test_sock = socket.socket()
    
    try:
        test_sock.bind(server_addr)
        test_sock.close()

        print("Запускаем сервер...")
        server_thread = threading.Thread(target=start_server, args=(server_addr,), daemon=False)
        server_thread.start()

        print("Подключаемся к нему же")
        connect_to_server(('127.0.0.1', server_port))
    except Exception as e:
        print("Не могу создать сервер - стало быть, уже есть. Подключаюсь")
        connect_to_server(server_addr)