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
    def __init__(nickName, ip, socket):
        self.nickName = nickName
        self.ip = ip
        self.socket = socket
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

          cliente = Client(nickname, addr, connectionSocket)
          self.clients.append(cliente)

          welcome = nicname + " acabou de entrar"

          send_for_all(welcome)

        serverSocket.close() # encerra o socket do servido


        """
        A thread principal irá recepcionar o usuário novo
        Perguntará o seu nick.

        Em sequência, ela enviara uma Tupla contendo o ip do usuário + nickname
        """
        pass

    def send_for_all(message):
        # ENVIAR PRA GALERA KKKKKKK
        try:
            for user in self.clients:
                user.socket.send(message)
        except Error:
            print ("ERROR ON CHAT -> %s" % Error)
        pass

    def chat():
        """
        Função do chat (SALVE JOAO DÓRIA Kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk???????)
        """

        print("Chat iniciado com sucesso")

        while 1:
            # RECEBER MENSAGEM
            message = self.socket.recv(1024)
            prompt = message.slice("(")
            directive = prompt[1].slice(")")

            # Tratar mensagem, para caso ser um comando

            if   prompt[1] == "lista":
                for user in self.clients:
                    send_for_all("<" + str(user.nick) +", " + str(user.IP) + ", " + str(user.socket))
            elif prompt[1] == "privado":

            elif prompt[1] == "nome":
                """BOTAR AQUI O NICK DO CLIENTE AGORA É NOVO-JOAO-DORIA"""
                send_for_all()
            elif prompt[1] == "sair":

                """ BOTAR AQUI QUE O CARA ACABOU DE SAIR, TEM QUE PEGAR O NOME DELE"""
                send_for_all()
            else:
                send_for_all(message)







        pass
