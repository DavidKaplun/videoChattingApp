import socket
import tkinter
import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time
import pyshine as ps
from random import randint
import socket, cv2, pickle, struct, time,imutils
from PIL import ImageTk, Image

PORT=6969
SERVER_HOST="DESKTOP-2J7HUUE"

WIDTH=750
HEIGHT=550


#for chats the window is 600 height 500 width
#for login and register 300 width 200 height
def client():
    global client_socket,root,flag_working,prev_message,ip_to_send_to
    prev_message=""
    ip_to_send_to=""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, int(PORT)))
    root = tk.Tk()
    root.geometry(str(WIDTH)+"x"+str(HEIGHT))
    root.title("David's App")
    root.resizable(0,0)
    root.configure(background="#333333")
    show_login_window()
    root.mainloop()
    client_socket.close()

def start_meeting_thread():
    meeting_thread=Thread(target=start_meeting)
    meeting_thread.start()
    print("meeting started")

def open_join_meeting_window():
    global join_window
    join_window = tk.Tk()
    join_window.geometry("300x150")
    join_window.title("Join Meeting")

    entry = tk.Entry(join_window)
    entry.place(x=100, y=50)

    text = tk.Label(join_window, text="Enter meeting link:")
    text.place(x=0, y=50)

    btn = tk.Button(join_window, text="Join",command=lambda:join_meeting_thread(entry.get()))
    btn.place(x=150, y=70)

    join_window.mainloop()

def join_meeting_thread(meeting_link):
    print(meeting_link)
    meeting_thread=Thread(target=join_meeting,args=[meeting_link])
    meeting_thread.start()
    print("join meeting")

def join_meeting(meeting_link):
    message_to_send=str(5)+","+meeting_link
    global send_to_ports
    send_to_ports=[]

    global ip_to_connect_to
    ip_to_connect_to=""

    send_message(message_to_send.encode())
    ip = socket.gethostbyname(socket.gethostname())

    while(len(send_to_ports)<4):
        if(len(send_to_ports)>0 and send_to_ports[0]==-1):
            return
        time.sleep(0.5)
    global join_window
    join_window.destroy()
    video_sending_port=send_to_ports[2]
    audio_sending_port=send_to_ports[3]
    video_receiving_port=send_to_ports[0]
    audio_receiving_port=send_to_ports[1]

    video_sending_thread = Thread(target=send_video, args=(ip, video_sending_port))
    audio_sending_thread = Thread(target=send_audio, args=(ip, audio_sending_port))

    video_receiving_thread = Thread(target=receive_video, args=(ip_to_connect_to, video_receiving_port))
    audio_receiving_thread = Thread(target=receive_audio, args=(ip_to_connect_to, audio_receiving_port))


    video_sending_thread.start()
    audio_sending_thread.start()

    video_receiving_thread.start()
    audio_receiving_thread.start()

def start_meeting():
    ports=create_ports()
    # ports[0] sending video port
    # ports[1] sending audio port
    # ports[2] receiving video port
    # ports[3] receiving audio port

    ip=socket.gethostbyname(socket.gethostname())

    meeting_link=generate_random_link()

    message_to_send=str(4)+","+meeting_link
    for port in ports:
        message_to_send+=","+str(port)
    message_to_send+=","+ip
    print(message_to_send)
    send_message(message_to_send.encode())

    video_sending_port=ports[0]
    audio_sending_port=ports[1]

    video_receiving_port=ports[2]
    audio_receiving_port=ports[3]

    messagebox.showinfo(title="Info", message="Meeting started. link:"+meeting_link)

    video_sending_thread=Thread(target=send_video,args=(ip, video_sending_port))
    audio_sending_thread=Thread(target=send_audio,args=(ip, audio_sending_port))

    video_sending_thread.start()
    audio_sending_thread.start()

    global ip_to_send_to
    while(ip_to_send_to==""):
        time.sleep(0.5)

    video_receiving_thread = Thread(target=receive_video, args=(ip_to_send_to, video_receiving_port))
    audio_receiving_thread = Thread(target=receive_audio, args=(ip_to_send_to, audio_receiving_port))

    video_receiving_thread.start()
    audio_receiving_thread.start()

def receive_audio(ip,port):
    ip=ip.replace(" ","")
    mode = 'get'
    name = 'CLIENT RECEIVING AUDIO'
    audio, context = ps.audioCapture(mode=mode)
    ps.showPlot(context, name)
    print("receiving audio function activated")
    # create socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    socket_address = (ip, port)
    client_socket.connect(socket_address)
    print("CLIENT CONNECTED TO", socket_address)
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        while len(data) < payload_size:
            packet = client_socket.recv(4 * 1024)  # 4K
            print("getting audio")
            if not packet: break
            data += packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        while len(data) < msg_size:
            data += client_socket.recv(4 * 1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        audio.put(frame)

    client_socket.close()

def receive_video(ip,port):
    ip=ip.replace(" ","")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))  # a tuple
    data = b""
    payload_size = struct.calcsize("Q")

    print("receiving video function activated")
    while True:
        while len(data) < payload_size:
            packet = client_socket.recv(4 * 1024)  # 4K
            if not packet: break
            data += packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]

        while len(data) < msg_size:
            data += client_socket.recv(4 * 1024)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        cv2.imshow("RECEIVING VIDEO", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    client_socket.close()




def send_video(ip,port):

    ip=ip.replace(" ","")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host_name = socket.gethostname()

    socket_address = (ip, port)
    server_socket.bind(socket_address)
    server_socket.listen(5)

    print("sending video function activated","LISTENING AT:", socket_address)

    while True:
        client_socket, addr = server_socket.accept()
        global ip_to_send_to
        ip_to_send_to = addr
        print('GOT CONNECTION FROM:', addr)
        if client_socket:
            vid = cv2.VideoCapture(0)

            while (vid.isOpened()):
                img, frame = vid.read()
                frame = imutils.resize(frame, width=320)
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)

                cv2.imshow('TRANSMITTING VIDEO', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    client_socket.close()


def send_audio(ip,port):
    ip=ip.replace(" ","")
    mode = 'send'
    name = 'SERVER TRANSMITTING AUDIO'
    audio, context = ps.audioCapture(mode=mode)
    # ps.showPlot(context,name)
    # Socket Create
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    backlog = 5
    socket_address = (ip, port)
    print('sending audio STARTING SERVER AT', socket_address, '...')
    server_socket.bind(socket_address)
    server_socket.listen(backlog)

    while True:
        client_socket, addr = server_socket.accept()
        global ip_to_send_to
        ip_to_send_to = addr
        print('GOT CONNECTION FROM:', addr)
        if client_socket:
            while (True):
                frame = audio.get()

                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)
        else:
            break
    client_socket.close()




def generate_random_link():
    link=""
    while(len(link)<12):
        char=chr(randint(ord('a'), ord('z')))
        link+=char
    return link

def create_ports():
    ports=[]
    while(len(ports)<4):
        str_num=""
        for j in range(4):
            num=randint(1, 9)
            str_num+=str(num)
        if str_num not in ports:
            ports.append(int(str_num))
    return ports

def show_error_message(message):
    if(message=="-1"):
        messagebox.showinfo(title="Info", message="Invalid request")
    else:
        message=message.split(",")
        messagebox.showinfo(title="Info", message=message[1])
        global send_to_ports
        send_to_ports.append(-1)

def send_message_to_user(message,message_entry):
    message_entry.delete(0,tk.END)
    message_to_send="2,"+username_of_current_user+","+send_to+","+message
    send_message(message_to_send.encode())

def recieve_and_respond(answer):
    if (answer[0] == "0" or answer == "-1"):
        show_error_message(answer)

    if(answer[0]=="2"):
        clear_window()
        root.minsize(width=500, height=600)
        show_users(answer[1:])

    elif(answer[0]=="3"):
        global prev_message
        if prev_message!=answer[1:]:
            clear_chat()
            root.minsize(width=500, height=600)
            show_chat(answer[1:])
            prev_message=answer[1:]

    elif(answer[0]=="5"):
        global send_to_ports
        answer=answer.split(",")
        answer=answer[1:]
        send_to_ports=[]
        for elem in answer:
            string=elem.replace("[","")
            string=string.replace("]","")
            string = string.replace("'","")
            if "." not in string:
                send_to_ports.append(int(string))
            else:
                global ip_to_connect_to
                ip_to_connect_to=string



def send_login_request(username,password):
    global username_of_current_user
    username_of_current_user = username
    send_message((str(1)+","+username+","+password).encode())

def send_register_request(username,password):
    global username_of_current_user
    username_of_current_user = username
    send_message((str(0)+","+username+","+password).encode())



def request_chat(name):
    global send_to
    while(flag_working):
        send_to=name
        send_message(("3," + name + "," + username_of_current_user).encode())
        time.sleep(0.1)

def get_chat(request_message):
    global flag_working
    flag_working = False
    # should wait 2 seconds
    time.sleep(0.2)
    flag_working=True
    print(request_message)
    client_thread = Thread(target=request_chat, args=[request_message])
    client_thread.start()


def send_message(message):
    client_socket.send(message)
    answer=client_socket.recv(1024).decode()
    recieve_and_respond(answer)


def clear_chat():
    for widget in root.winfo_children():
        if isinstance(widget,tkinter.Label):
            widget.destroy()



def show_login_window():
    clear_window()
    #The Title
    heading = tk.Label(root,text="Welcome to David's app",fg='white',font=('yu gothic ui', 20, "bold"),bd=5,bg="#333333")
    heading.place(x=80,y=30,width=300,height=30)

    #The Left image
    left_side_image=Image.open("C:\\Users\\user\\Downloads\\images\\vector.png")
    photo=ImageTk.PhotoImage(left_side_image)
    image_label = tk.Label(root,image=photo,bg="#333333")
    image_label.image=photo
    image_label.place(x=5,y=100,width=500,height=450)

    #Sign In Image
    sign_in_image=Image.open("C:\\Users\\user\\Downloads\\images\\hyy.png")
    photo = ImageTk.PhotoImage(sign_in_image)
    sign_in_image_label = tk.Label(root, image=photo,bg="#333333")
    sign_in_image_label.image = photo
    sign_in_image_label.place(x=500,y=70)

    #Sign In Label
    sign_in_label = tk.Label(root, text="Sign In", bg="#333333",font=("yu gothic ui", 17, "bold"),fg="white")
    sign_in_label.place(x=530,y=180)

    #Username
    username_label = tk.Label(root,text="Username",bg="#333333",font=("yo gothic ui",13),fg="white")
    username_label.place(x=475,y=240)

    username_entry = tk.Entry(root,bg="#333333",fg="white",relief=tk.FLAT,font=("yu gothic ui", 12, "bold"),insertbackground = 'white')
    username_entry.place(x=505,y=270,width=270)

    username_line = tk.Canvas(root,width=200,height=0,bg='white')
    username_line.place(x=475,y=300)

    #Username icon
    username_icon = Image.open("C:\\Users\\user\\Downloads\\images\\username_icon.png")
    photo = ImageTk.PhotoImage(username_icon)
    username_icon_label = tk.Label(root,image=photo,bg="#333333")
    username_icon_label.image=photo
    username_icon_label.place(x=475,y=270)


    #Login button
    login_button_img = Image.open("C:\\Users\\user\\Downloads\\images\\btn1.png")
    photo = ImageTk.PhotoImage(login_button_img)

    button_label = tk.Label(root,image=photo,bg='#333333')
    button_label.image = photo
    button_label.place(x=435,y=440)

    login_button = tk.Button(button_label,text='LOGIN',bd=0, font=("yu gothic ui", 13, "bold"), width=25,relief=tk.FLAT, height=1,bg='#3047ff', cursor='hand2', activebackground='#3047ff', fg='white',command=lambda:send_login_request(username_entry.get(),password_entry.get()))
    login_button.place(x=20,y=10)

    #Password
    password_label = tk.Label(root,text="Password",bg="#333333", fg="white", font=("yu gothic ui", 13, "bold"))
    password_label.place(x=475,y=330)

    password_entry = tk.Entry(root, relief=tk.FLAT, bg="#333333", fg="white",font=("yu gothic ui", 12, "bold"), show="*", insertbackground = 'white')
    password_entry.place(x=505,y=360,width=270)

    password_line = tk.Canvas(root,width=200,height=0,bg="#333333")
    password_line.place(x=475, y=390)

    #Password icon
    password_icon = Image.open("C:\\Users\\user\\Downloads\\images\\password_icon.png")
    photo = ImageTk.PhotoImage(password_icon)

    password_icon_label = tk.Label(root,image=photo,bg='#333333')
    password_icon_label.image=photo

    password_icon_label.place(x=475,y=360)

    #Don't have an account label
    dont_have_account_label=tk.Label(root,text="Don't Have an Account?",font=("yu gothic ui", 12),bg="#333333",fg="white")
    dont_have_account_label.place(x=450,y=515)

    #Create An Account button
    register_button_img = Image.open("C:\\Users\\user\\Downloads\\images\\register.png")
    photo = ImageTk.PhotoImage(register_button_img)

    button_register_label = tk.Button(root, image=photo,bd=0, bg='#333333',cursor='hand2',relief=tk.FLAT,command=lambda:show_register_window(),activebackground='#333333')
    button_register_label.image = photo
    button_register_label.place(x=625, y=515,height=30,width=115)


def show_register_window():
    clear_window()
    # The Title
    heading = tk.Label(root, text="Welcome to David's app", fg='white', font=('yu gothic ui', 20, "bold"), bd=5,
                       bg="#333333")
    heading.place(x=80, y=30, width=300, height=30)

    # The Left image
    left_side_image = Image.open("C:\\Users\\user\\Downloads\\images\\vector.png")
    photo = ImageTk.PhotoImage(left_side_image)
    image_label = tk.Label(root, image=photo, bg="#333333")
    image_label.image = photo
    image_label.place(x=5, y=100, width=500, height=450)

    # Sign In Image
    sign_in_image = Image.open("C:\\Users\\user\\Downloads\\images\\hyy.png")
    photo = ImageTk.PhotoImage(sign_in_image)
    sign_in_image_label = tk.Label(root, image=photo, bg="#333333")
    sign_in_image_label.image = photo
    sign_in_image_label.place(x=500, y=70)

    # Sign Up Label
    sign_in_label = tk.Label(root, text="Sign Up", bg="#333333", font=("yu gothic ui", 17, "bold"), fg="white")
    sign_in_label.place(x=530, y=180)

    # Username
    username_label = tk.Label(root, text="Username", bg="#333333", font=("yo gothic ui", 13), fg="white")
    username_label.place(x=475, y=240)

    username_entry = tk.Entry(root, bg="#333333", fg="white", relief=tk.FLAT, font=("yu gothic ui", 12, "bold"),
                              insertbackground='white')
    username_entry.place(x=505, y=270, width=270)

    username_line = tk.Canvas(root, width=200, height=0, bg='white')
    username_line.place(x=475, y=300)

    # Username icon
    username_icon = Image.open("C:\\Users\\user\\Downloads\\images\\username_icon.png")
    photo = ImageTk.PhotoImage(username_icon)
    username_icon_label = tk.Label(root, image=photo, bg="#333333")
    username_icon_label.image = photo
    username_icon_label.place(x=475, y=270)

    # Login button should be register button
    register_button_img = Image.open("C:\\Users\\user\\Downloads\\images\\btn1.png")
    photo = ImageTk.PhotoImage(register_button_img)

    button_label = tk.Label(root, image=photo, bg='#333333')
    button_label.image = photo
    button_label.place(x=435, y=440)

    register_button = tk.Button(button_label, text='REGISTER', bd=0, font=("yu gothic ui", 13, "bold"), width=25, relief=tk.FLAT, height=1, bg='#3047ff', cursor='hand2', activebackground='#3047ff', fg='white', command=lambda: send_register_request(username_entry.get(), password_entry.get()))
    register_button.place(x=20, y=10)

    # Password
    password_label = tk.Label(root, text="Password", bg="#333333", fg="white", font=("yu gothic ui", 13, "bold"))
    password_label.place(x=475, y=330)

    password_entry = tk.Entry(root, relief=tk.FLAT, bg="#333333", fg="white", font=("yu gothic ui", 12, "bold"), show="*", insertbackground='white')
    password_entry.place(x=505, y=360, width=270)

    password_line = tk.Canvas(root, width=200, height=0, bg="#333333")
    password_line.place(x=475, y=390)

    # Password icon
    password_icon = Image.open("C:\\Users\\user\\Downloads\\images\\password_icon.png")
    photo = ImageTk.PhotoImage(password_icon)

    password_icon_label = tk.Label(root, image=photo, bg='#333333')
    password_icon_label.image = photo

    password_icon_label.place(x=475, y=360)

    # Don't have an account label should be already have an account
    already_have_account_label = tk.Label(root, text="Already Have an Account?", font=("yu gothic ui", 12), bg="#333333", fg="white")
    already_have_account_label.place(x=440, y=515)

    # Create An Account button should be login button
    register_button_img = Image.open("C:\\Users\\user\\Downloads\\images\\register.png")
    photo = ImageTk.PhotoImage(register_button_img)

    button_register_label = tk.Label(root, image=photo,bg='#333333')
    button_register_label.image = photo
    button_register_label.place(x=625, y=515, height=30, width=115)

    button_register = tk.Button(button_register_label,bd=0,activebackground='#39bee1', text="LOGIN HERE",bg='#39bee1',font=("yu gothic ui", 9), cursor='hand2',relief=tk.FLAT, command=lambda: show_login_window(),fg="white")
    button_register.place(x=20,y=5,height=15)

def show_users(names):
    names=names.split(",")
    for i in range(len(names)):
        btn=tk.Button(root,height=4,width=25, text=names[i],command=lambda k=names[i]:get_chat(k))
        btn.place(x=0, y=60*i)

    message_entry=tk.Entry(root,width=35)
    message_entry.place(x=230,y=550)

    send_btn=tk.Button(root, text="SEND",command=lambda:send_message_to_user(message_entry.get(),message_entry))
    send_btn.place(x=450, y=545)

    start_meeting_btn = tk.Button(root, text="START MEETING",command=start_meeting_thread)
    start_meeting_btn.place(x=230, y=20)

    join_meeting_btn = tk.Button(root, text="JOIN MEETING",command=open_join_meeting_window)
    join_meeting_btn.place(x=350, y=20)

    w = tk.Canvas(root, width=1, height=600)
    w.configure(background="black")
    w.place(x=180,y=0)

    w = tk.Canvas(root, width=330, height=1)
    w.configure(background="black")
    w.place(x=183, y=50)


def clear_window():
    for widgets in root.winfo_children():
        widgets.destroy()

def show_chat(chat):
    chat=chat.split(",")
    print(chat)
    for i in range(0,len(chat),2):
        txt = tk.Label(root,height=2, text=chat[i])
        txt.pack()
        txt.place(x=200, y=i*20+20)
    w = tk.Canvas(root, width=330, height=1)
    w.configure(background="black")
    w.place(x=183, y=50)

client()

#client protocols:

#register - 0,username,password
#login - 1,username,password
#sendMessage - 2,username,username
