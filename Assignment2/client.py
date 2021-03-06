from socket import *
import threading
class SendingThread(threading.Thread):
    '''
    Thread client uses to send messages to another users(Technically to server which forwards to appropriate receicver.)
    '''
    def __init__(self,ClientSocketToSend):
        threading.Thread.__init__(self)
        self.ClientSocketToSend = ClientSocketToSend
        return
    def run(self):
        while True:
            message = ''
            dest = ''
            inp = input()
            if (inp[0]!='@'):
                print("Incorrect message sending format. Please enter again", flush = True)
                continue
            else:
                inp = inp[1:]
                data = inp.split()
                if len(data)<2:
                    print("Incorrect message sending format. Please try again", flush = True)
                    continue
                else:
                    dest = data[0]
                    message = inp[len(data[0])+1:]
            # print("Enter message to Send" , flush=True)
            # message = input()
            # dest = input("Enter destination:")
            message_formated = "SEND "+dest+'\n'+'Content-length: '+str(len(message))+"\n\n"+message+'\n'
            self.ClientSocketToSend.send(message_formated.encode())
            reply = self.ClientSocketToSend.recv(1024)#Check the status of the sent message.
            reply = reply.decode()
            if(reply == "ERROR 103 Header incomplete\n\n"):
                print("Header incomplete. Some issue on application side. Please re-registor. If problem persists install updated application")
                self.ClientSocketToSend.close()
                Register()
                break
            else:
                data = reply.split()
                print("DATA = ", data , flush=True)
                if data[0] == 'SEND':
                    continue
                else:
                    print("Error, message could not be delivered. Please check the intended username", flush=True)

                    
class ReceivingThread(threading.Thread):
    '''
    Thread client uses to receive message from other users.
    '''
    def __init__(self,ClientSocketToReceive):
        threading.Thread.__init__(self)
        self.ClientSocketToReceive = ClientSocketToReceive
        return 
    def run(self):
        while True:
            try:
                message = self.ClientSocketToReceive.recv(1024)   
            except:
                print('Socket closed. Closing the thread')
                return
            message = message.decode()
            data = message.split()
            s = message[message.find('\n\n'):]
            s = s.strip('\n') 
            if(len(data)<= 0 or data[2]!='Content-length:' or len(s)!=int(data[3])):
                print("Content-length ",data[3], 'messagelength = ', len(s), flush=True)
                msg = 'ERROR 103 Incomplete Header\n\n'
                self.ClientSocketToReceive.send(msg.encode())
                continue
            print("Message from: ", data[1]," : ",end = '',flush=True)   
            print(s,flush=True)      
            msg = 'RECEIVED '+data[1]+'\n\n'
            self.ClientSocketToReceive.send(msg.encode())
def Register():
    '''
    Register the client.
    '''
    ClientSocketToSend = socket(AF_INET, SOCK_STREAM)
    ClientSocketToSend.connect((serverName, serverPort))
    while True:
        reg = "REGISTER TOSEND "
        print("Enter user name:", flush=True)
        usr_name = input()
        reg+= usr_name+'\n\n'
        ClientSocketToSend.send(reg.encode())
        message = ClientSocketToSend.recv(1024)
        message = message.decode()
        data = message.split()
        print(message)
        if data[0] == "REGISTERED":
            break
        elif message == 'ERROR 101 No user registered\n\n' or message == "Incorrect registration\n\n":
            ClientSocketToSend.close()
            ClientSocketToSend = socket(AF_INET, SOCK_STREAM)
            ClientSocketToSend.connect((serverName,serverPort))
    ClientSocketToReceive = socket(AF_INET, SOCK_STREAM)
    ClientSocketToReceive.connect((serverName, serverPort))
    reg = 'REGISTER TORECV '+usr_name+"\n\n"
    print("Sending message TO server about registering", flush=True)
    ClientSocketToReceive.send(reg.encode())
    print("Message sent",flush=True)
    message = ClientSocketToReceive.recv(1024).decode()
    data = message.split()
    if data[0] == "REGISTERED":
        print("Registration Completed",flush=True)
        st = SendingThread(ClientSocketToSend)
        rt = ReceivingThread(ClientSocketToReceive)
        st.start()
        rt.start()
    else:
        print("Some error, Try changing username and reapply",flush=True)    


serverName = input('Enter IPaddress or DNS: ')
serverPort = 18000
Register()