from Encoder import Encoder
from socket import socket, AF_INET, SOCK_DGRAM
import os


SERVER_IP = '127.0.0.1'
SERVER_PORT = 8002

class Server:
    SERVER_IP = SERVER_IP
    SERVER_PORT = SERVER_PORT

    def __init__(self):
        print("Initializing server...")
        print("Use CTRL+C to stop Server\n")
        self.ip = self.SERVER_IP
        self.port = self.SERVER_PORT
        self.file_name = ""
        self.initServer()

    def initServer(self):
        try:
            with socket(AF_INET, SOCK_DGRAM) as s:
                s.settimeout(0.5)
                # só binda (escuta pacotes) a porta, sem estabelecer conexão
                s.bind((self.ip, self.port))

                while True:
                    try:
                        req, addr = s.recvfrom(Encoder.BYTES_SIZE["msg"])
                    except:
                        continue

                    decoded = Encoder.decode(req)

                    # Sem "estado", decide ação de acordo com header
                    if decoded["type"] == "GET":
                        self.processGet(decoded["data"].decode(), s, addr)
                    if decoded["type"] == "RET":
                        self.processRet(s, decoded["id"], addr)
        except KeyboardInterrupt:
            print("Server stopped running!")

    def processRet(self, socket, id, addr):
        print(f"Retrieving lost package with id: {id}...")
        with open(f".{self.file_name}", "rb") as f:
            file_data = f.read()
            P_SIZE = Encoder.BYTES_SIZE["payload"]
            index = id * P_SIZE
            payload = file_data[index-P_SIZE:index]
            self.send(socket, "DATA", payload, id, addr)
        print(f"Lost package {id} sent!\n")

    def processGet(self, file_name, socket, addr):
        self.file_name = file_name
        P_SIZE = Encoder.BYTES_SIZE["payload"]
        try:
            with open(f".{file_name}", "rb") as f:
                print("Sending file...")
                file_data = f.read()
                file_len = len(file_data)

                total_seg = file_len // P_SIZE
                if len(file_data) % P_SIZE > 0:
                    total_seg += 1

                # Informa total de segmentos a receber
                self.send(socket, "INFO", str(total_seg).encode(), addr=addr)

                id_segm = 1
                for i in range(0, len(file_data), P_SIZE):
                    payload = file_data[i:i+P_SIZE]

                    self.send(socket, "DATA", payload, id_segm, addr)
                    id_segm += 1

                # Header END: o fim da transmissão
                self.send(socket, "END", "", addr=addr)
        except FileNotFoundError:
            print(f"File {file_name} not found...")
            self.send(socket, "ERR", "", addr=addr)

        print("All packages were sent to client!")

    def send(self, socket, type, msg, header=0, addr=None):
        socket.sendto(Encoder.encode(header, type, msg), addr)
