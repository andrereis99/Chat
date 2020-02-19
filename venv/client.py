"""
 Implements a simple socket client

"""

import socket
import threading
import tkinter
import time

# Define socket host and port
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000
msg_text = ''
msg_list = ''

class Counter:
    def __init__(self):
        self.counter = 0

    def getCounter(self):
        return self.counter

    def setCounter(self,n):
        self.counter = n

counter = Counter()

# Create socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server
client_socket.connect((SERVER_HOST, SERVER_PORT))

def sendMsg(event=None):
    # Send message
    msg = msg_text.get()
    msg_text.set('')
    client_socket.sendall(msg.encode())


    # Check for exit
    if msg == 'exit':
        counter.setCounter(1)

def receives_thread(client_socket):
    while counter.getCounter() == 0:
        res = client_socket.recv(1024).decode()
        msg_list.insert(tkinter.END, res)

    # Close socket
    client_socket.close()
    top.quit()



def on_closing(event=None):
    msg_text.set("exit")
    sendMsg()


#interface
top = tkinter.Tk()
frame = tkinter.Frame(top)
msg_text = tkinter.StringVar()
msg_text.set('Insert Username')
scrollbar = tkinter.Scrollbar(frame)
msg_list = tkinter.Listbox(frame, height=15, width=90, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
frame.pack()

entry_field = tkinter.Entry(top, textvariable=msg_text)
entry_field.bind("<Return>", sendMsg)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=sendMsg)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)


# Cria thread
thread = threading.Thread(target=receives_thread, args=(client_socket,))
thread.start()

tkinter.mainloop()

while True:
    msg_list.insert(tkinter.END, 'Insert username: ')
    username = msg_text.get()

    if username == 'exit':
        on_closing()
        break

    client_socket.sendall(username.encode())
    res = client_socket.recv(1024).decode()
    msg_list.insert(tkinter.END, res)
    if res != 'Invalid username' or res != 'Username is in use':
        break
