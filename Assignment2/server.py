from socket import *
import threading
UsernameToPortSend = {}
UsernameToPortRcv = {}
serverPort = 18000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen()
print("The server is ready to receive")
class RegisteringThreadSend(threading.Thread):
    def __init__(self,connectionSocket,username):
        threading.Thread.__init__(self)
        self.connectionSocket = connectionSocket
        self.username = username
        return
    def validate(self):
        for i in self.username:
            if(0<=ord(i)-ord('A')<=25 or 0<=ord(i)-ord('a')<=25 or 0<=ord(i)-ord('0')<=9):
                continue
            else:
                return False 
        return True        
    def run(self):
        b = self.validate()
        if not b or self.username in UsernameToPortSend.keys():
            msg = 'ERROR 100 Malformed username\n\n'
            self.connectionSocket.send(msg.encode())
        else:
            UsernameToPortSend[self.username] = self.connectionSocket
            msg = "REGISTERED TOSEND "+self.username+"\n\n"
            self.connectionSocket.send(msg.encode())  
            while True:
                msg = self.connectionSocket.recv(1024)
                msg = msg.decode()
                '''
                Parsing the message. For now let us print the whole message and not care about the format.
                '''
                data = msg.split()
                print(msg,flush=True)
                if data[1] not in UsernameToPortSend.keys():
                    msg = "ERROR 102 Unable to send\n\n"
                    self.connectionSocket.send(msg.encode())
                elif not data[3].isdigit():
                    msg = 'ERROR 103 Header incomplete\n\n'
                    self.connectionSocket.send(msg.encode())
                    UsernameToPortSend.pop(self.username)
                    self.connectionSocket.close()
                    UsernameToPortRcv.pop(self.username)
                    return 
                else:
                    sendingSocket = UsernameToPortRcv[data[1]] 

                    sendingSocket.send(msg.encode())#Dont forget to add conditions of forward etc.
                    msg = sendingSocket.recv(1024)
                    msg = msg.decode()
                    data = msg.split()
                    if data[0] == "RECEIVED":
                        msg = 'SEND '+data[1]+"\n\n"
                        self.connectionSocket.send(msg.encode())

class RegisteringThreadRecv(threading.Thread):
    def __init__(self, connectionSocket, username):
        threading.Thread.__init__(self)
        self.connectionSocket = connectionSocket
        self.username = username
        return
    def run(self):
        if(self.username not in UsernameToPortSend.keys()):
            print("Some kind of error has occured:", flush= True)
            msg = 'ERROR 100 Malformed Username'    
            self.connectionSocket.send(msg.encode())
        else:
            UsernameToPortRcv[self.username] = self.connectionSocket
            msg = "REGISTERED TORECV "+self.username+'\n\n'
            self.connectionSocket.send(msg.encode())
            print("Sending Port registration Succes", flush=True)
            
                


def ServerProgrammeStart():
    while True:
        connectionSocket, addr = serverSocket.accept()
        print("Connection succesful", flush=True)
        message = connectionSocket.recv(1024)
        message = message.decode()
        print("Message ", message,flush=True)
        data = message.split()
        if data[0] == "REGISTER":
            if data[1] == 'TOSEND':
                print("Registering sender socket", flush= True)
                rt = RegisteringThreadSend(connectionSocket,data[2])
                rt.start()
                print("Registration Complete", flush=True)
            elif data[1] == 'TORECV':
                print("Registering Receiving Socket",flush=True)
                rcv_rt = RegisteringThreadRecv(connectionSocket, data[2])
                rcv_rt.start()
            else:
                reply = "ERROR 100 Malformed username\n\n"
                connectionSocket.send(reply)      
ServerProgrammeStart()                               