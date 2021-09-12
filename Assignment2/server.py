from socket import *
import threading
RESERVED_KEYWORDS = ['SEND', 'ALL', 'REGISTER', 'TOSEND', 'TORECV', 'FORWARD', 'REGISTERED', 'ERROR']
UsernameToPortSend = {}
UsernameToPortRcv = {}
serverPort = 18000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen()
print("The server is ready to receive")
def extract_username(message):
    '''
    Given message in the specified format, it extracts username from the message.

    Parameters:
    message: Message of the form REGISTER TORECV/TOSEND Username\n\n

    Returns:
    Username.
    '''
    data = message.split()
    if(len(data)<=2):
        return '@'
    else:
        le = len(data[0])+1+len(data[1])+1
        ans = message[le:-2]
        return ans      
class SendingThread(threading.Thread):
    '''
    Thread server uses to forward messages from a socket.
    '''
    def __init__(self,connectionSocket, sender, message, receiver):
        '''
        Thread initialization. Specifying various fields the thread needs to run.

        Parameters:
        connectionSocket: The connection socket between the server and the receiver's Receiver socket.
        sender: The username of the sender of the message.
        receiver: The username of the receiver of the message.
        
        Returns:
        An instance of the SendingThread.
        '''
        threading.Thread.__init__(self)
        self.connectionSocket = connectionSocket
        self.sender = sender
        self.message = message
        self.receiver = receiver
    def run(self):
        '''
        Send the message to the intended user and then reterieve the confirmation message.
        '''
        data = self.message.split()
        msg = 'FORWARD '+self.sender+'\n'+data[2]+' '+data[3]+'\n\n'+self.message[self.message.find('\n\n')+2:]
        self.connectionSocket.send(msg.encode())
        msg = self.connectionSocket.recv(1024).decode()
        data = msg.split()
        if data[0] == 'RECEIVED':
            senderSocket = UsernameToPortSend[self.sender]
            msg = 'SEND '+self.receiver+'\n\n'
            senderSocket.send(msg.encode())
        else:
            senderSocket = UsernameToPortSend[self.sender]
            msg = 'ERROR 102 Unable to send\n\n'
            senderSocket.send(msg.encode())    
class BroadcastSendingThread(threading.Thread):
    '''
    Thread used for broadcasting messages to all users.
    '''
    def __init__(self, connectionSocket, sender, message, receiver):
        '''
        Thread initialization. Specifying various fields thread needs to run.
        
        Parameters:
        connectionSocket: The connection socket between the server and the receiver's Receiver socket.
        sender: The username of the sender of the message.
        receiver: The username of the receiver of the message.
        
        Returns:
        An instance of the BroadcastSendingThread.
        '''
        threading.Thread.__init__(self)
        self.connectionSocket = connectionSocket
        self.sender = sender
        self.message = message
        self.receiver = receiver
    def  run(self):
        '''
        Send the message to the intended user and then reterieve the confirmation message.
        '''
        data = self.message.split()
        msg = 'FORWARD '+self.sender+'\n'+data[2]+' '+data[3]+'\n\n'+self.message[self.message.find('\n\n'):].strip()
        self.connectionSocket.send(msg.encode())
        msg = self.connectionSocket.recv(1024).decode()
        data = msg.split()
class RegisteringThreadSend(threading.Thread):
    '''
    Thread used for registering sending socket of a user.
    '''
    def __init__(self,connectionSocket,username):
        '''
        Thread Initialization
        Parameters:
        connectionSocket: The connection socket between the client sending socket and the server.
        username: The username of the client.
        Returns:
        An instance of RegesteringThreadSend.
        '''
        threading.Thread.__init__(self)
        self.connectionSocket = connectionSocket
        self.username = username
        return
    def validate(self):
        '''
        Validate a username.
        Check it contains only [A-Z],[a-z] and [0-10]. No special characters and spaces are used.
        '''
        for i in self.username:
            if(0<=ord(i)-ord('A')<=25 or 0<=ord(i)-ord('a')<=25 or 0<=ord(i)-ord('0')<=9):
                continue
            else:
                return False 
        if self.username in RESERVED_KEYWORDS:
            return False  
        return True        
    def run(self):
        '''
        Register the user and wait for incoming messages from the client. Spawn Sending threads whenever message is received.
        '''
        b = self.validate()
        if not b or self.username in UsernameToPortSend.keys():
            msg = 'ERROR 100 Malformed username\n\n'
            self.connectionSocket.send(msg.encode())
            while True:
                msg = self.connectionSocket.recv(1024)
                msg = msg.decode()
                data = msg.split()
                if len(data)<=1:
                    msg = 'ERROR 101 No user registered\n\n'
                    self.connectionSocket.send(msg.encode())
                elif data[0] !='REGISTER':
                    msg =   'ERROR 100 Malformed username\n\n'
                    self.connectionSocket.send(msg.encode())
                else:
                    self.username = data[2]
                    b = self.validate()
                    if not b or self.username in UsernameToPortSend.keys():
                        msg = 'ERROR 100 Malformed username\n\n'
                        self.connectionSocket.send(msg.encode())
                    else:
                        break    
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
            if(len(data)<3):
                msg = 'ERROR 103 Header incomplete\n\n'
                self.connectionSocket.send(msg.encode())
                UsernameToPortSend.pop(self.username)
                self.connectionSocket.close()
                UsernameToPortRcv.pop(self.username)
                return
            if data[1] not in UsernameToPortSend.keys() and data[1]!='ALL':
                msg = "ERROR 102 Unable to send\n\n"
                self.connectionSocket.send(msg.encode())
            elif not data[3].isdigit() or not data[2] == 'Content-length:':
                msg = 'ERROR 103 Header incomplete\n\n'
                self.connectionSocket.send(msg.encode())
                UsernameToPortSend.pop(self.username)
                self.connectionSocket.close()
                UsernameToPortRcv.pop(self.username)
                return 
            elif data[1]=='ALL':
                '''
                We will spawn sending threads for sending messages. The threads will then wait for confirmation and ensure that the message is sent
                Broadcasting threads will be used
                '''   
                threads = []
                for i in UsernameToPortRcv.keys():
                    if i!=self.username:
                        st = BroadcastSendingThread(UsernameToPortRcv[i],self.username,msg,i)
                        threads.append(st)
                for thread in threads:
                    thread.start()
                msg = 'SEND '+data[1]+"\n\n"
                self.connectionSocket.send(msg.encode())        
            else:
                '''
                We will spawn a sending thread for sending message
                normal sending threads will be used
                '''
                sendingSocket = UsernameToPortRcv[data[1]] 
                st = SendingThread(sendingSocket,self.username,msg,data[1])
                st.start()
                # sendingSocket.send(msg.encode())#Dont forget to add conditions of forward etc.
                # msg = sendingSocket.recv(1024)
                # msg = msg.decode()
                # data = msg.split()
                # if data[0] == "RECEIVED":
                #     msg = 'SEND '+data[1]+"\n\n"
                #     self.connectionSocket.send(msg.encode())  

class RegisteringThreadRecv(threading.Thread):
    '''
    Thread used for registering receiving socket of a user.
    '''
    def __init__(self, connectionSocket, username):
        threading.Thread.__init__(self)
        self.connectionSocket = connectionSocket
        self.username = username
        return
    def run(self):
        if(self.username not in UsernameToPortSend.keys()):
            msg = 'ERROR 100 Malformed Username'    
            self.connectionSocket.send(msg.encode())
        else:
            UsernameToPortRcv[self.username] = self.connectionSocket
            msg = "REGISTERED TORECV "+self.username+'\n\n'
            self.connectionSocket.send(msg.encode())
            
                


def ServerProgrammeStart():
    '''
    Start of the server programme.
    '''
    while True:
        connectionSocket, addr = serverSocket.accept()
        message = connectionSocket.recv(1024)
        message = message.decode()
        data = message.split()
        if data[0] == "REGISTER":
            if data[1] == 'TOSEND':
                rt = RegisteringThreadSend(connectionSocket,extract_username(message))
                rt.start()
            elif data[1] == 'TORECV':
                rcv_rt = RegisteringThreadRecv(connectionSocket, extract_username(message))
                rcv_rt.start()
            else:
                reply = "Incorrect registration\n\n"
                connectionSocket.send(reply.encode())      
        else:
            reply = 'ERROR 101 No user registered\n\n' 
            connectionSocket.send(reply.encode())     
ServerProgrammeStart()                               