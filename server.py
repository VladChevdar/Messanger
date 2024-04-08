from datetime import datetime
import subprocess
import threading
import socket
import server
import sys

# Simple in-memory storage
users = {}  # username: password
friends = {}  # username: [list of messages]

HOST = 'localhost'
PORT = 5050
lock = threading.Lock()

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])

weather_bot = "Weather-Bot"
#Default members
users["Vlad"] = "~on" #friend requests on
friends["Vlad"] = {"Pasha": []}
users["Pasha"] = "~on"
friends["Pasha"] = {"Vlad": []}
active_users = []

def handle_client(conn, addr):
    display_chat_command = True
    login_user = None
    while True:
        try:
            # Receive data from client
            data = conn.recv(1024).decode()
            if not data:
                break  # No data, close connection

            if data[:7] != "GETCHAT" or display_chat_command:
                if len(data) > 50:
                    print(data[:50] + "...")
                else:
                    print(data)
                display_chat_command = False

            if data[:11] == "SHOWFRIENDS":
                display_chat_command = True

            command, *args = data.split('|')
            if command == "SIGNUP":
                username, password = args
                with lock:
                    if username in users:
                        conn.send("Username already exists".encode())
                    else:
                        users[username] = password + '~on'
                        friends[username] = {}  # Initialize as an empty dictionary for friends and messages
                        conn.send("Signup successful".encode())
            elif command == "LOGIN":
                username, password = args
                with lock:
                    if username in users and users[username].split('~')[0] == password:
                        conn.send("Login successful".encode())
                        login_user = username
                        if username not in active_users:
                            active_users.append(username)
                    else:
                        conn.send("Invalid username or password".encode())
            elif command == "FRIEND_REQUESTS":
                username = args[0]
                with lock:
                    if users[username].split('~')[1] == 'on':
                        conn.send("on".encode())
                    else:
                        conn.send("off".encode())
            elif command == "IS_USER_ONLINE":
                print(active_users)
                username = args[0]
                with lock:
                    if username in active_users:
                        conn.send("Yes".encode())
                    else:
                        conn.send("No".encode())
            elif command == "CHECK_FOR_NOTIFICATION":
                username, friendname = args
                with lock:
                    if friendname in friends[username]:
                        messages = friends[username][friendname]
                        # Check if there are messages and more than one message
                        if messages and len(messages) > 1:
                            # Check all messages except the last one for ":Unread Message"
                            unread_exists = any(":Unread Messages" in message for message in messages[:-1])
                            if unread_exists:
                                conn.send("NEW_MESSAGE".encode())
                            else:
                                conn.send("NO_NEW_MESSAGES".encode())
                        else:
                            # If no messages or only one message, treat it as no new messages
                            conn.send("NO_NEW_MESSAGES".encode())
                    else:
                        conn.send("Friend not found.".encode())
            elif command == "READ_MESSAGES":
                username, friendname = args
                with lock:
                    if friendname in friends[username]:
                        try:
                            # Attempt to remove the ":Unread Messages" marker from the chat history
                            friends[username][friendname].remove(":Unread Messages")
                            conn.send("Unread message marker removed.".encode())
                        except ValueError:
                            # The ":Unread Messages" marker was not found in the chat history
                            conn.send("No unread message marker to remove.".encode())
                    else:
                        conn.send("Friend not found.".encode())
            elif command == "FRIEND_OFF":
                username, friendname = args
                with lock:
                    if friendname in friends[username]:
                        # ':' reprsents system sent message
                        friends[username][friendname].append(f":Unread Messages")
                        conn.send("Message sent".encode())
                    else:
                        conn.send("Friend not found".encode())
            elif command == "FRIENDSCOUNT":
                username = args[0]
                with lock:
                    if username not in friends:
                        conn.send(f"None".encode())
                    else:
                        num_friends = len(friends[username])
                        conn.send(f"{num_friends}".encode())
            elif command == "DELETE_FRIEND":
                username, friendname = args
                with lock:
                    if friendname in friends[username]:
                        del friends[username][friendname]
                        conn.send("Friend deleted".encode())

                        # remove the user from the friend's friend list
                        if friendname in friends and username in friends[friendname]:
                            del friends[friendname][username]
                    else:
                        conn.send("Friend is not in friend list".encode())
            elif command == "CHANGE_FRIEND_REQUESTS":
                username = args[0]
                with lock:
                    if users[username].split('~')[1] == 'on':
                        users[username] = users[username].split('~')[0] + '~off'
                        conn.send("Friend requests blocked".encode())
                    else:
                        users[username] = users[username].split('~')[0] + '~on'
                        conn.send("Friend requests unblocked".encode())

            elif command == "ADDFRIEND":
                username, friendname = args
                if username == friendname:
                    conn.send("Cannot add yourself".encode())
                with lock:
                    if friendname == weather_bot:
                            if friendname in friends[username]:
                                conn.send("Bot already added".encode())
                            else:
                                friends[username][friendname] = []
                                conn.send("Friend added".encode())
                    else:
                        if friendname in users:
                            if friendname not in friends[username]:
                                if users[friendname].split('~')[1] == 'off':
                                    conn.send("User blocked friend requests".encode())
                                    continue
                                friends[username][friendname] = []
                                conn.send("Friend added".encode())
                            if username not in friends[friendname]:
                                friends[friendname][username] = []
                            else:
                                conn.send("Friend already added".encode())
                        else:
                            conn.send("User not found".encode())
            elif command == "SHOWFRIENDS":
                username = args[0]
                with lock:
                    if friends[username]:
                        friends_list = "\n".join(friends[username].keys())
                        conn.send(friends_list.encode())
                    else:
                        conn.send("No friends".encode())
            elif command == "CLEAR_MESSAGES":
                username, friendname = args
                with lock:
                    if friendname in friends[username]:
                        friends[username][friendname] = []
                        conn.send("Messages cleared".encode())
            elif command == "REPORT_WEATHER":
                input_data = args[0]
                input_data = input_data.replace('~', '\n')
                with lock:
                    result = subprocess.run(['python3', 'Wbot.py'], input=input_data,
                                        capture_output=True, text=True, check=True)
                conn.send(result.stdout.encode())
            elif command == "SENDMESSAGE":
                username, friendname, message = args
                with lock:
                    if friendname in friends[username]:
                        # in case two login sessions but one disconnects
                        try:
                            friends[username][friendname].remove(":Unread Messages")
                        except ValueError:
                            pass
                        current_time = datetime.now()
                        time_str = current_time.strftime("%I:%M %p")
                        # '+' reprsents user sent message
                        friends[username][friendname].append('+' + f"{message} {time_str}")
                        if username in friends[friendname]:
                            # '-' reprsents received message
                            friends[friendname][username].append('-' + f"{message} {time_str}")
                        conn.send("Message sent".encode())
                    else:
                        conn.send("Friend not found".encode())
            elif command == "GETCHAT":
                username, friendname, last_message = args
                with lock:
                    if (friendname in friends[username] and friends[username][friendname] and 
                        len(friends[username][friendname]) > 0):

                        if len(friends[username][friendname]) == 1 and friends[username][friendname][0] == ":Unread Messages":
                            del friends[username][friendname][0]
                            conn.send("NO_MESSAGES".encode())
                        else:
                            messages_list = friends[username][friendname]
                            unread_message_found = ":Unread Messages" in messages_list
                            if last_message == '':
                                all_messages = "|".join(messages_list)
                                msg_size = len(all_messages)
                                if msg_size <= 10000:
                                    conn.send(all_messages.encode())
                                else:
                                    bytes_to_remove = msg_size - 10000
                                    # Find the first '|' occurring after the bytes_to_remove point
                                    split_point = all_messages.find('|', bytes_to_remove)

                                    if split_point != -1:
                                        if ":Unread Messages|" not in all_messages[split_point + 1:] and unread_message_found:
                                            conn.send((":Unread Messages|" + all_messages[split_point + 1:]).encode())
                                        else:
                                            conn.send(all_messages[split_point + 1:].encode())
                                    else:
                                        conn.send(":Messages too large to display".encode())
                            else:
                                # Initialize last_message_index to None
                                last_message_index = None
                                # Iterate backwards through messages_list to find the last occurrence of last_message
                                for i in range(len(messages_list) - 1, -1, -1):
                                    if messages_list[i] == last_message:
                                        last_message_index = i
                                        break
                                
                                # If last_message was found
                                if last_message_index is not None:
                                    # Slice the list to get only new messages after the last occurrence
                                    new_messages = messages_list[last_message_index + 1:]
                                    
                                    if new_messages:
                                        all_messages = "|".join(new_messages)
                                        conn.send(all_messages.encode())
                                    else:
                                        conn.send("NO_NEW_MESSAGES".encode())
                                else:
                                    # Handle the case where last_message is not found in the list
                                    conn.send("NO_NEW_MESSAGES".encode())
                    else:
                        conn.send("NO_MESSAGES".encode())
            elif command == "LOGOUT":
                with lock:
                    try:
                        print(login_user)
                        active_users.remove(login_user)
                        conn.send("Session closed".encode())
                    except ValueError:
                        conn.send("Inactive sesion".encode())
        except:
            # Handle client disconnect
            with lock:
                try:
                    active_users.remove(login_user)
                except ValueError:
                    pass
                break  
    
    conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Server started on {HOST}:{PORT}. Waiting for connections...")
    while True:
        conn, addr = server.accept()
        print(f"Connection from {addr}")
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()