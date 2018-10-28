# UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE
# DEPARTAMENTO DE ENGENHARIA DE COMPUTACAO E AUTOMACAO
# DISCIPLINA REDES DE COMPUTADORES (DCA0113)
# AUTOR: ...
#
# SCRIPT: ...

# importacao das bibliotecas
from socket import *                       # sockets
from threading import Thread


class Connected(Thread):
    def __init__(nickName, socket, addr):
        Thread.__init__(self)
        self.nickName = nickName
        self.socket = socket
        self.ip  = addr[0]
        self.port= addr[1]
    def run(self): #metodo para a thread
        while True:
            frame  = socket.recv(56) # todo frame ocupa no maximo 56 bytes


        self.socket.close()
    def send(self,msg, dest): #dest eh outro Connected

        self.socket.send(len(msg).encode('UTF-8')) #tamanho da mensagem
        self.socket.send(self.ip.encode('UTF-8'))  #ip de origem da mensagem
        self.socket.send(dest.ip.encode('UTF-8'))  #ip destino
        self.socket.send(self.nickName.encode('UTF-8'))
        self.socket.send(b'0')
        self.socket.send(msg.encode('UTF-8'))

class Server(Thread):
    def __init__(self,port):
        Thread.__init__(self)
        # configura o servidor
        self.serverName = ''                            # ip do servidor (em branco)
        self.serverPort = port                         # porta a se conectar
        self.serverSocket = socket(AF_INET,SOCK_STREAM) # criacao do socket TCP
        self.serverSocket.bind((serverName,serverPort)) # bind do ip do servidor com a porta
        # inicia o servidor
        self.connecteds = list()#vetor de client

        self.finish = False
    def run(self):
        # função para chamar a thread do bate papo
        print ('Servidor TCP esperando conexoes na porta %d ...' % (serverPort))
        self.serverSocket.listen(1)                     # socket pronto para 'ouvir' conexoes
        self.manager(serverSocket)

    def manager(self,serverSocket):
        # Gerencia os usuários

        while not self.finish:
          connectionSocket, addr = self.serverSocket.accept() # aceita as conexoes dos clientes
          nickname = connectionSocket.recv(1024)

          if len(nickname) == 0:
              connectionSocket.close()
              continue

          connected = Connected(nickname, addr, connectionSocket)

          self.clients.append(connected)
          welcome = nickname + "\nacabou de entrar\n"
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
