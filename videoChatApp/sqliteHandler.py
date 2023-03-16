import sqlite3

SUCCESS=1
FAILURE=0

EMPTY=0


def register(username,password):
    connection = sqlite3.connect("chatApp.db")
    search_command = "SELECT * FROM users WHERE username='" + username+"'"

    cur = connection.cursor()
    cur.execute(search_command)
    answer=cur.fetchall()
    if(len(answer)==EMPTY):
        insert_command="INSERT INTO users VALUES('"+username+"','"+password+"')"
        cur.execute(insert_command)
        connection.commit()
        connection.close()
        return "2"+get_users(username)
    connection.close()
    return str(FAILURE)+",username already exists"

def get_users(username):
    connection = sqlite3.connect("chatApp.db")
    search_command = "SELECT username FROM users WHERE NOT username='" + username + "' LIMIT 10;"

    cur = connection.cursor()
    cur.execute(search_command)

    users=cur.fetchall()
    list_users=[]
    for username in users:
        list_users.append(username[0])

    return ','.join(list_users)

def login(username,password):
    connection = sqlite3.connect("chatApp.db")
    search_command = "SELECT * FROM users WHERE username='" + username + "'"

    cur = connection.cursor()
    cur.execute(search_command)
    answer = cur.fetchall()
    connection.close()
    if (len(answer) > EMPTY):
        if(answer[0][0]==username and answer[0][1]==password):
            return "2"+get_users(username)
    return str(FAILURE)+",password or username incorrect"

def save_message(user_from,second_username,message):
    connection = sqlite3.connect("chatApp.db")
    cur=connection.cursor()
    table_name = get_table_name(user_from,second_username)

    create_chat(user_from, second_username)
    insert_command = "INSERT INTO "+table_name+" (messagefrom,message) VALUES('" + user_from + "','" + message + "')"
    cur.execute(insert_command)
    connection.commit()
    connection.close()

def read_messages_from_database(username,second_username):
    connection = sqlite3.connect("chatApp.db")
    cur = connection.cursor()
    table_name = get_table_name(username, second_username)
    create_chat(username,second_username)
    search_command = "SELECT messagefrom,message FROM "+table_name+" ORDER BY id DESC LIMIT 12;"

    cur.execute(search_command)
    messages=cur.fetchall()
    connection.close()
    messages=messages[::-1]
    message_list=[]
    for message in messages:
        message_list.append(message[0])
        message_list.append(message[1])
    return ','.join(message_list)



def create_chat(username,second_username):
    connection = sqlite3.connect("chatApp.db")
    cur = connection.cursor()
    table_name=get_table_name(username, second_username)

    create_command="CREATE TABLE IF NOT EXISTS "+table_name+"(id INTEGER PRIMARY KEY AUTOINCREMENT, messagefrom TEXT, message TEXT)"

    cur.execute(create_command)
    connection.commit()
    connection.close()


def get_table_name(username,second_username):
    table_name = ""
    if (username < second_username):
        table_name += username + second_username
    else:
        table_name += second_username + username
    table_name += "messages"
    return table_name


