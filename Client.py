import os
from Encoder import Encoder
from Server import SERVER_IP, SERVER_PORT
from socket import socket, AF_INET, SOCK_DGRAM
import random

class Client:

    def __init__(self, debugCheckFile = False):
        print("Initializing client...\n")
        self.debugCheckFile = debugCheckFile
        self.running = True
        while self.running:
            self.getInput()
            try:
                self.getFile()
            except FileNotFoundError:
                continue

    def getInput(self):
        requiring_path = True
        while requiring_path:
            shell_input = input("Please type file path '{IP}:{PORT}/{filename}' or 'exit' to quit: ")

            if shell_input in ["exit", "quit", "/q", ":wq"]:
                self.running = False
                return

            if self.debugCheckFile and shell_input == "":
                shell_input = f"{SERVER_IP}:{SERVER_PORT}/files/in"

            if shell_input.count(":") < 1 or shell_input.count("/") < 1:
                print("Invalid Path!!!")
                requiring_path = True
            else:
                server_ip = shell_input[0:shell_input.find(":")]
                server_port = shell_input[shell_input.find(":")+1:shell_input.find("/")]
                filename = shell_input[shell_input.find("/"):]

                if filename == "":
                    print("Invalid Path!!!")
                    requiring_path = True
                else:
                    requiring_path = False


        self._transmitting = False
        self._ip = server_ip
        self._port = int(server_port)
        self._fname = filename

    def getFile(self):
        if not self.running:
            return

        with socket(AF_INET, SOCK_DGRAM) as s:
            # Primeiro pacote enviado como pedido ao servidor
            payload = Encoder.encode(0, "GET", self._fname.encode())
            s.sendto(payload, (self._ip, self._port))
            self._transmitting = True

            file = {}
            loss = []
            segm_count = 0

            print("Receiving packages...")
            while self._transmitting:
                try:
                    # recvfrom dados e endereço de quem enviou
                    msg, addr = s.recvfrom(Encoder.BYTES_SIZE["msg"])
                except Exception as e:
                    print("No connection stablished. Server not innitialized!")
                    return

                decoded = Encoder.decode(msg)
                self.processDecoded(decoded, file, loss, segm_count)

            # UDP não garante entrega, nem ordem dos pacotes, necessário recuperar perdas do lado do cliente
            self.retrieveLosses(loss, file, s)
            self.writeFile(file, './files/out')

    def retrieveLosses(self, loss, file, socket):
        print(f"Retrieving {len(loss)} packages lost\n")
        while len(loss) > 0:
            # Cliente envia um pedido explícito de retransmissão ao servidor
            print(f"Requiring lost package with id: {loss[0]}...")
            ret_msg = Encoder.encode(loss[0], "RET", "".encode())
            socket.sendto(ret_msg, (self._ip, self._port))
            msg, addr = socket.recvfrom(Encoder.BYTES_SIZE["msg"])
            decoded = Encoder.decode(msg)

            if decoded["type"] == "DATA":
                if decoded["id"] == loss[0]:
                    # Se chegou correto, armazena e remove da lista de perdas
                    if Encoder.CRC_32(decoded["data"]) == decoded["crc32"]:
                        file[loss[0]] = decoded["data"]
                        print(f"Lost package {loss[0]} recovered!\n")
                        loss.pop(0)

    def processDecoded(self, decoded, file, loss, segm_count):
        data = decoded["data"]
        id = decoded["id"]

        if decoded["type"] == "ERR":
            print("File not found!!!")
            raise FileNotFoundError()


        if decoded["type"] == "INFO":
            segm_count = int(decoded["data"])
            print(f"Number of packages: {segm_count}\n")

        if decoded["type"] == "DATA":
            segm_count = id if segm_count <= 0 else segm_count

            # Simulação de perdas para teste do checksum
            if random.randint(1, 16) == 1:
                data = data[id-5:id]

            if Encoder.CRC_32(data) != decoded["crc32"]:
                loss.append(id)
            else:
                file[id] = data

        if decoded["type"] == "END":
            # Checa completude de segmentos
            for i in range(1, segm_count):
                if i not in file:
                    loss.append(i)
            self._transmitting = False

    def writeFile(self, file, output):
        print("Writing output file...")
        with open(output, "wb") as f:
            for seg_id in sorted(file.keys()):
                f.write(file[seg_id])

        print("File written!\n")

        if self.debugCheckFile:
            file1 = output
            file2 = f".{self._fname}"

            with open(file1, "rb") as f1, open(file2, "rb") as f2:
                if f1.read() == f2.read():
                    print("File complete")
                else:
                    print("File incomplete")
