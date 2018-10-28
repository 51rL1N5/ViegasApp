from socket import *                       # sockets
from classes import *
import pickle

host = '127.0.0.1'
port = 2626

client = socket(AF_INET,SOCK_STREAM)
client.connect(tuple([host,port]))

nickName = input('Informe seu nick Name:\t')
client.send(nickName.encode('utf-8'))

while True:
    msg = input('Digite:\t')
    frame = Frame('50.50.50.50', '40.40.40.40', nickName, 0, msg)
    client.send( pickle.dumps(frame))

    if not msg:break

client.close()
print('conexao encerrada')
