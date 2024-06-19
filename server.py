from datetime import datetime
import subprocess
import threading
import socket
import server
import sys

# Simple in-memory storage
users = {}  # username: password
friends = {}  # username: {friendname: [list of messages]}
live_button = {}  # username: {friendname: value}
active_users = []

HOST = 'localhost'
PORT = 5050
lock = threading.Lock()

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])

# Default members
users["Vlad"] = "~on"  # friend requests on
friends["Vlad"] = {"Pasha": []}
users["Pasha"] = "~on"
friends["Pasha"] = {"Vlad": []}

# Bots
weather_bot = "Weather Bot"
numbers_game = "Numbers Game"
bots = [weather_bot, numbers_game]

def send_response(conn, message):
    conn.send(message.encode())

def handle_signup(conn, args):
    username, password = args
    with lock:
        if username in users:
            send_response(conn, "Username already exists")
        else:
            users[username] = password + '~on'
            friends[username] = {}  # Initialize as an empty dictionary for friends and messages
            send_response(conn, "Signup successful")

def handle_login(conn, args):
    username, password = args
    with lock:
        if username in users and users[username].split('~')[0] == password:
            send_response(conn, "Login successful")
            if username not in active_users:
                active_users.append(username)
            return username
        else:
            send_response(conn, "Invalid username or password")
    return None

def handle_update_live_button(conn, args):
    username, friendname = args
    if friendname in live_button and username in live_button[friendname]:
        send_response(conn, live_button[friendname][username])
    else:
        send_response(conn, "0")

def handle_set_live_button(conn, args):
    username, friendname, value = args
    with lock:
        if username in live_button:
            live_button[username][friendname] = value
        else:
            live_button[username] = {friendname: value}
        send_response(conn, "Live button set")

def handle_friend_requests(conn, args):
    username = args[0]
    with lock:
        if users[username].split('~')[1] == 'on':
            send_response(conn, "on")
        else:
            send_response(conn, "off")

def handle_is_user_online(conn, args):
    username = args[0]
    with lock:
        if username in active_users:
            send_response(conn, "Yes")
        else:
            send_response(conn, "No")

def handle_check_for_notification(conn, args):
    username, friendname = args
    with lock:
        if friendname in friends[username]:
            messages = friends[username][friendname]
            unread_exists = any(":Unread Messages" in message for message in messages[:-1])
            if unread_exists:
                send_response(conn, "NEW_MESSAGE")
            else:
                send_response(conn, "NO_NEW_MESSAGES")
        else:
            send_response(conn, "Friend not found.")

def handle_read_messages(conn, args):
    username, friendname = args
    with lock:
        if friendname in friends[username]:
            try:
                friends[username][friendname].remove(":Unread Messages")
                send_response(conn, "Unread message marker removed.")
            except ValueError:
                send_response(conn, "No unread message marker to remove.")
        else:
            send_response(conn, "Friend not found.")

def handle_friend_off(conn, args):
    username, friendname = args
    with lock:
        if friendname in friends[username]:
            friends[username][friendname].append(":Unread Messages")
            send_response(conn, "Message sent")
        else:
            send_response(conn, "Friend not found")

def handle_friends_count(conn, args):
    username = args[0]
    with lock:
        if username not in friends:
            send_response(conn, "None")
        else:
            num_friends = len(friends[username])
            send_response(conn, f"{num_friends}")

def handle_delete_friend(conn, args):
    username, friendname = args
    with lock:
        if friendname in friends[username]:
            del friends[username][friendname]
            send_response(conn, "Friend deleted")
            if friendname in friends and username in friends[friendname]:
                del friends[friendname][username]
        else:
            send_response(conn, "Friend is not in friend list")

def handle_change_friend_requests(conn, args):
    username = args[0]
    with lock:
        if users[username].split('~')[1] == 'on':
            users[username] = users[username].split('~')[0] + '~off'
            send_response(conn, "Friend requests blocked")
        else:
            users[username] = users[username].split('~')[0] + '~on'
            send_response(conn, "Friend requests unblocked")

def handle_add_friend(conn, args):
    username, friendname = args
    if username == friendname:
        send_response(conn, "Cannot add yourself")
    with lock:
        if friendname in bots:
            if friendname in friends[username]:
                send_response(conn, "Bot already added")
            else:
                friends[username][friendname] = []
                send_response(conn, "Friend added")
        else:
            if friendname in users:
                if friendname not in friends[username]:
                    if users[friendname].split('~')[1] == 'off':
                        send_response(conn, "User blocked friend requests")
                        return
                    friends[username][friendname] = []
                    send_response(conn, "Friend added")
                if username not in friends[friendname]:
                    friends[friendname][username] = []
                else:
                    send_response(conn, "Friend already added")
            else:
                send_response(conn, "User not found")

def handle_show_friends(conn, args):
    username = args[0]
    with lock:
        if friends[username]:
            friends_list = "\n".join(friends[username].keys())
            send_response(conn, friends_list)
        else:
            send_response(conn, "No friends")

def handle_clear_messages(conn, args):
    username, friendname = args
    with lock:
        if friendname in friends[username]:
            friends[username][friendname] = []
            send_response(conn, "Messages cleared")

def handle_report_weather(conn, args):
    input_data = args[0].replace('~', '\n')
    with lock:
        result = subprocess.run(['python3', 'Wbot.py'], input=input_data,
                                capture_output=True, text=True, check=True)
        send_response(conn, result.stdout)

def handle_send_message(conn, args):
    username, friendname, message = args
    with lock:
        if friendname in friends[username]:
            try:
                friends[username][friendname].remove(":Unread Messages")
            except ValueError:
                pass
            current_time = datetime.now()
            time_str = current_time.strftime("%I:%M %p")
            friends[username][friendname].append(f'+{message} {time_str}')
            if username in friends[friendname]:
                friends[friendname][username].append(f'-{message} {time_str}')
            send_response(conn, "Message sent")
        else:
            send_response(conn, "Friend not found")

def handle_get_chat(conn, args):
    username, friendname, last_message = args
    with lock:
        if friendname in friends[username] and friends[username][friendname]:
            messages_list = friends[username][friendname]
            unread_message_found = ":Unread Messages" in messages_list

            if last_message == '':
                all_messages = "|".join(messages_list)
                msg_size = len(all_messages)
                if msg_size <= 10000:
                    send_response(conn, all_messages)
                else:
                    bytes_to_remove = msg_size - 10000
                    split_point = all_messages.find('|', bytes_to_remove)
                    if split_point != -1:
                        if ":Unread Messages|" not in all_messages[split_point + 1:] and unread_message_found:
                            send_response(conn, ":Unread Messages|" + all_messages[split_point + 1:])
                        else:
                            send_response(conn, all_messages[split_point + 1:])
                    else:
                        send_response(conn, ":Messages too large to display")
            else:
                last_message_index = None
                for i in range(len(messages_list) - 1, -1, -1):
                    if messages_list[i] == last_message:
                        last_message_index = i
                        break

                if last_message_index is not None:
                    new_messages = messages_list[last_message_index + 1:]
                    if new_messages:
                        all_messages = "|".join(new_messages)
                        send_response(conn, all_messages)
                    else:
                        send_response(conn, "NO_NEW_MESSAGES")
                else:
                    send_response(conn, "NO_NEW_MESSAGES")
        else:
            send_response(conn, "NO_MESSAGES")

def handle_logout(conn, login_user):
    with lock:
        try:
            active_users.remove(login_user)
            send_response(conn, "Session closed")
        except ValueError:
            send_response(conn, "Inactive session")

def handle_client(conn, addr):
    display_chat_command = True
    login_user = None
    while True:
        try:
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
                handle_signup(conn, args)
            elif command == "LOGIN":
                login_user = handle_login(conn, args)
            elif command == "UPDATE_LIVE_BUTTON":
                handle_update_live_button(conn, args)
            elif command == "SET_LIVE_BUTTON":
                handle_set_live_button(conn, args)
            elif command == "FRIEND_REQUESTS":
                handle_friend_requests(conn, args)
            elif command == "IS_USER_ONLINE":
                handle_is_user_online(conn, args)
            elif command == "CHECK_FOR_NOTIFICATION":
                handle_check_for_notification(conn, args)
            elif command == "READ_MESSAGES":
                handle_read_messages(conn, args)
            elif command == "FRIEND_OFF":
                handle_friend_off(conn, args)
            elif command == "FRIENDSCOUNT":
                handle_friends_count(conn, args)
            elif command == "DELETE_FRIEND":
                handle_delete_friend(conn, args)
            elif command == "CHANGE_FRIEND_REQUESTS":
                handle_change_friend_requests(conn, args)
            elif command == "ADDFRIEND":
                handle_add_friend(conn, args)
            elif command == "SHOWFRIENDS":
                handle_show_friends(conn, args)
            elif command == "CLEAR_MESSAGES":
                handle_clear_messages(conn, args)
            elif command == "REPORT_WEATHER":
                handle_report_weather(conn, args)
            elif command == "SENDMESSAGE":
                handle_send_message(conn, args)
            elif command == "GETCHAT":
                handle_get_chat(conn, args)
            elif command == "LOGOUT":
                handle_logout(conn, login_user)
        except Exception as e:
            # Handle client disconnect or any other exceptions
            print(f"Exception: {e}")
            with lock:
                try:
                    if login_user in active_users:
                        active_users.remove(login_user)
                except ValueError:
                    pass
                break

    conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server started at {HOST}:{PORT}")

        while True:
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_server()