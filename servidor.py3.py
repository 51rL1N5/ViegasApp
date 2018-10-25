# UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE
# DEPARTAMENTO DE ENGENHARIA DE COMPUTACAO E AUTOMACAO
# DISCIPLINA REDES DE COMPUTADORES (DCA0113)
# AUTOR: ...
#
# SCRIPT: ...

# importacao das bibliotecas
from socket import *                       # sockets
from threading import Thread


class Client(threading.Thread):
    def __init__(nickName, ip, port):
        self.nickName = nickName
        self.ip = ip
        self.port = port
        # self.socket = socket(AF_INET, SOCK_STREAM)
        # self.socket.bind(PORT)
        # flag para comunicacao privada ?
        # nick do usuario com quem este esta em privado ?
        pass
    def run(): #metodo para a thread
        pass



class Server(threading.Thread):
    def __init__(port):
        # configura o servidor
        self.serverName = ''                            # ip do servidor (em branco)
        self.serverPort = port                         # porta a se conectar
        self.serverSocket = socket(AF_INET,SOCK_STREAM) # criacao do socket TCP
        self.serverSocket.bind((serverName,serverPort)) # bind do ip do servidor com a porta
        # inicia o servidor
        self.clients = []#vetor de client
    def run():
        # função para chamar a thread do bate papo
        # ASDFADFADFAFDASFADSFASD()

        self.serverSocket.listen(1)                     # socket pronto para 'ouvir' conexoes

        print ('Servidor TCP esperando conexoes na porta %d ...' % (serverPort))

        # -------------------
        self.manager(serverSocket);
        # --- manager == main

    def manager(serverSocket):
        # Gerencia os usuários

        while True:
          connectionSocket, addr = self.serverSocket.accept() # aceita as conexoes dos clientes

          nickname = connectionSocket.recv(1024)

          if len(nickname) == 0:
              connectionSocket.close()
              continue

          self.clients.append([nickname, addr, connectionSocket])

        serverSocket.close() # encerra o socket do servido



        self.clients.append( Client(Nick, IP, port) );

        """
        A thread principal irá recepcionar o usuário novo
        Perguntará o seu nick.

        Em sequência, ela enviara uma Tupla contendo o ip do usuário + nickname
        """
        pass
