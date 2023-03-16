import socket
from threading import Thread
from sqliteHandler import *

HOST=socket.gethostname()
PORT=6969

REGISTER=0
LOGIN=1
SENDMESSAGE=2
READCHAT=3
START_MEETING=4
JOIN_MEETING=5

meetings={}

def server():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind((HOST,PORT))
    server_socket.listen(5)
    while True:
        client_socket, client_port=server_socket.accept()
        client_thread=Thread(target=handle_client,args=(client_socket, client_port,))
        client_thread.start()


def handle_client(client_socket, client_port):
    while True:
        data = client_socket.recv(1024)
        answer=answer_for_client(data.decode())
        print(data.decode(),answer)
        client_socket.send(answer.encode())


def answer_for_client(message):
    message=message.split(",")
    if(valid_input(message)==False):
        return "-1"

    message_option=ord(message[0])-48
    if(message_option==REGISTER):
        username = message[1]
        password= message[2]
        answer=register(username,password)
        return answer

    elif (message_option == LOGIN):
        username = message[1]
        password = message[2]
        answer = login(username, password)
        return answer

    elif(message_option==SENDMESSAGE):
        return send_message(message)

    elif(message_option==READCHAT):
        return read_messages(message)

    elif(message_option==START_MEETING):
        save_meeting(message)
        return str(SUCCESS)

    elif(message_option==JOIN_MEETING):
        if(message[1] in meetings):
            return str(5)+","+str(meetings[message[1]])
        return "0,meeting link invalid"

def save_meeting(message):
    key=message[1]
    value=message[2:]
    meetings[key]=value
    print(key,value)

def send_message(message):
    userfrom = message[1]
    userto = message[2]
    message_from_user = message[3]
    save_message(userfrom, userto, message_from_user)
    return read_messages(message)

def read_messages(message):
    username = message[1]
    another_username = message[2]
    messages = read_messages_from_database(username, another_username)
    return "3,"+messages

def valid_input(message):
    if(len(message)<2):
        return False
    message_option=ord(message[0])-48
    print(message_option)
    if(message_option>=REGISTER and message_option<=JOIN_MEETING):
        return True
    return False


server()