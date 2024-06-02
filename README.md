# Real-Time Chat Application with Bots

This real-time chat application enables users to sign up, log in, manage friends, send messages, and interact with bots  
such as Weather Bot" and "Numbers Game". The system uses Python sockets for network communication and multithreading  
to handle multiple client connections simultaneously, ensuring real-time interaction.  

## Features
**User Management:** Users can sign up, log in, and update their status.  
**Friend Management:** Users can send friend requests, delete friends, and view their friend lists.  
**Real-Time Messaging:** Send and receive messages instantly.  
**Bot Interaction:** Engage with built-in bots for additional functionality like weather reports and games.  
**Notifications:** Real-time notifications for new messages and changes in friend status.

### Installation
1. Clone the repository:
  > git clone [repository URL]

#### Usage
To start the server:
  > python server.py [Optional: Port Number]

#### Server and Client Commands ( no spaces between '|' character )
**SIGNUP | username | password**                 =>  _Registers a new user._  
**LOGIN | username | password:**                =>  _Logs in an existing user._  
**ADDFRIEND | username | friendname:**           =>   _Adds a new friend._  
**SENDMESSAGE | username | friendname | message:** => _Sends a message._  
**SHOWFRIENDS | username:**                    => _Displays the friend list of the user._  
**LOGOUT:**                                  => _Closes the user session._  

##### Technologies
**Python:** Core programming language used.  
**Socket Programming:** For client-server communication.  
**Threading:** To handle multiple client connections concurrently.  

###### System Architecture
The application consists of a server module and a client module. The server handles all incoming connections,  
processes client requests, and manages data storage in memory. The client module interacts with the server via   
commands and handles user inputs and outputs.

