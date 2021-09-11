from socket import *
import threading
class SendingThread(threading.Thread):
    def __init__(self,ClientSocketToSend):
        self.ClientSocketToSend = ClientSocketToSend
        return
    def run(self):
        while True:
            message = input("Enter Message to send:")
            dest = input("Enter destination:")
            message_formated = "SEND "+dest+'\n'+'Content-length:'+str(len(message))+"\n\n"
            self.ClientSocketToSend.send(message_formated.encode())
            reply = self.ClientSocketToSend.recv(1024)
            reply = reply.decode()
            if(reply == "ERROR 103 Header incomplete\n\n"):
                exit
class ReceivingThread(threading.Thread):
    def __init__(self,ClientSocketToReceive):
        self.ClientSocketToReceive = ClientSocketToReceive
        return 
    def run(self):
        while True:
            message = self.ClientSocketToReceive.recv(1024)   
            message = message.decode()
            data = message.split()
            assert(len(data)>=3 and data[2].isdigit())
            s = ''
            l = len(data[0])+1+len(data[1]+1+len(data[2]))
            for i in range(l, l+int(data[2])):
                s+=message[i]
            print("Message from: ", data[1],":",end = '')    
            print(s)    
        exit    
                


serverName = 'localhost'
serverPort = 18000
ClientSocketToSend = socket(AF_INET, SOCK_STREAM)
ClientSocketToSend.connect((serverName, serverPort))
usr_name = ''

while True:
    reg = "REGISTER TOSEND "
    usr_name = input("Enter username:")
    reg+= usr_name+'\n\n'
    ClientSocketToSend.send(reg.encode())
    message = ClientSocketToSend.recv(1024)
    message = message.decode()
    data = message.split()
    if data[0] == "RESGISTERED":
        break


ClientSocketToReceive = socket(AF_INET, SOCK_STREAM)
ClientSocketToReceive.connect((serverName, serverPort))
reg = 'RESGISTER TORECV '+usr_name+"\n\n"
ClientSocketToSend.send(reg.encode())
message = ClientSocketToReceive.recv(1024).decode()
data = message.split()



ClientSocketToSend.send(reg.encode())
message = ClientSocketToReceive.recv(1024).decode()
data = message.split()
if data[0] == "REGISTERED":
    st = SendingThread(ClientSocketToSend)
    rt = ReceivingThread(ClientSocketToReceive)
    st.start()
    rt.start()
