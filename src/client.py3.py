from socket import *                       # sockets


host = '127.0.0.1'
port = 3131

client = socket(AF_INET,SOCK_STREAM)
client.connect(tuple([host,port]))

while True:
    msg = input('Digite:\t')
    if not msg:break
    client.send(msg.encode('UTF-8'))


client.close()
print('conexao encerrada')
