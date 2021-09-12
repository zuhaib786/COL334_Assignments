# Assignment 2 COL334 Computer Networks
## Author: Zuhaib Ul Zamann
## Date: 10/09/2021
### Client.py
This is the client side implementation of the application. The application first starts by registering sending socket at the server side with a username. If the resgistration is successful, then the receiving socket is registered.<br>
After the registration is complete, two threads are created.<br>
One for receiving and one for sending
1. The sending thread waits for user input. After the user inputs some message to be delivered, the thread asks for the username of the person to whom the message is to be delivered.<br>
1. The thread then sends the message to the server and lets server to handle the forwarding of the message while waiting for the response from the server.<br>
1. The Receiving thread waits for any incoming messages coming from the users via server and then gives appropriate response to the server for delivering the message.<br>
1. Client side application includes checks for incoming messages regarding the header format and size of the message delivered.
1. In case of __ERROR 103__ the thread exits exiting the client programme.
1. The application then needs to restart and re-register to be able to send messages.
### Server.py
This is the server side implementation of the application. The server first starts by binding socket to local host(127.0.0.1) at port number __18000__.Then the socket starts listening.
1. Whenever an incoming connection request comes, the server ensures that the incoming request is of type registering. If any other type of message comes, then the server throws an error(ERROR 101 No user registered).
1. When the incoming message is of registration, the server thread invokes the corresponding registartion thread(RegisteringThreadSend for sending socket registration and RegesteringThreadRecv for receiving socket regestration). Two hashtables are mantained for mapping usernames to their respective sending and receiving port.
1. The regestering thread for receiving socket closes once registration is done, while for sending socket remains active.
1. The sending thread continuously waits for the client to send the message to be delivered to another user.
1. When the  client sends a message to be delivered to another user, the registering thread for send spawns a sending thread which then carries the proceess of sending it to the appropriate receiver and giving appropriate responses in case any mishap occurs.
1. Appropriate checks are made to ensure formatting of incoming messages follow the protocol.
1. This code does not take care of concurrency and synchornization issues that may occur.
