# import modules
import socket
import threading
from tkinter import *
from tkinter import messagebox
import tkinter
from tkinter import simpledialog
from tkinter import scrolledtext
from tkinter import ttk
import re
import algorithm
import time
import pickle
from pathlib import Path

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090


class Client:
    def __init__(self, host, port):
        self.connected_user = []
        self.from_keys = {}
        self.my_keys = {}
        self.selected_user = ""

        global notif

        # Start Connection to the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        # make a window with tkinter
        msg = tkinter.Tk()
        msg.withdraw()
        self.sock.send('USERLIST'.encode('ascii'))
        userlist = pickle.loads(self.sock.recv(1024))
        # asking the client to input their Nickname
        while True:
            try:
                user_already = ''
                self.nama_val = simpledialog.askstring("Nickname", "Enter your nickname: ", parent=msg)
                self.nickname = re.sub(r'[^a-zA-Z0-9]', '', self.nama_val)
                for i in userlist:
                    if str(self.nickname).strip('\n') == i:
                        user_already = 'yes'
                if user_already == 'yes':
                    notif = "username already exist"
                    user_already = ''
                elif self.nickname[0:2].isdigit():
                    notif = "Name can't start with numbers!"
                elif len(self.nickname) == 0:
                    notif = "Name can't be empty!"
                elif len(self.nickname) < 5 or len(self.nickname) >= 30:
                    notif = "Name is too short/long!"
                else:
                    # just saying to let the program don't move on to the next section of the app (Not Logged in yet)
                    self.gui_ready = False
                    # The program is running
                    self.running = True
                    break
            except NameError as ex:
                messagebox.showerror("ERROR", ex)
            except Exception as ex:
                messagebox.showerror("Error", ex)
            messagebox.showinfo("Notif", notif)

        # setting a thread between the UI and the Receive Func so that when def Receive didn't receive anyhting
        # the UI is still there running by their own time/term, so both thread runs by their own time without having
        # to wait for the other one
        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    # function to give combobox a purpose
    def selected_combobox(self, event):
        print("user selected:", self, event)
        self.selected_user = self.cb_user.get()
        self.enc_input.delete(0, END)
        key = 0
        if self.selected_user in self.my_keys:
            key = self.my_keys[self.selected_user]
        self.enc_input.insert(0, key)

    # function for the main UI
    def gui_loop(self):
        # UI main window where you can just put any widgets in here
        self.win = tkinter.Tk()
        self.win.title(self.nickname)
        self.win.config(bg="pink")

        # Disconnect Button
        self.disc_button = tkinter.Button(self.win, text='Disconnect', bg='red', fg='white', height=1, width=10,
                                          command=self.stop)
        self.disc_button.config(font=('Arial', 12))
        self.disc_button.pack(side=TOP, padx=10, pady=5)

        # History Chat Button
        self.history_button = tkinter.Button(self.win, text='History-Chat', bg='lightblue', height=1, width=10,
                                             command=self.load_text_history)  # TODO
        self.history_button.config(font=('Arial', 12))
        self.history_button.pack(side=TOP, padx=10, pady=5)

        # Chat Label
        self.chat_label = tkinter.Label(self.win, text='Chat:', bg='pink')
        self.chat_label.config(font=('Arial', 12))
        self.chat_label.pack(padx=20, pady=5)

        # Chat Box
        self.chat_box = tkinter.scrolledtext.ScrolledText(self.win, height=20)
        self.chat_box.config(state='disabled')
        self.chat_box.pack(padx=20, pady=5)

        # Message Label
        self.msg_label = tkinter.Label(self.win, text='Write your message:', bg='pink')
        self.msg_label.config(font=('Arial', 12))
        self.msg_label.pack(padx=20, pady=5)

        # Message Input
        self.msg_input = tkinter.Text(self.win, height=1, width=50)
        self.msg_input.pack(padx=20, pady=5)

        # Send Button
        self.send_button = tkinter.Button(self.win, text="Send", bg="lightblue", width=10, command=self.write)
        self.send_button.pack(pady=5, padx=20)
        self.send_button.config(font=('Arial', 12))

        # Combo Box For Showing Online User
        self.cb_user = ttk.Combobox(self.win)
        self.cb_user.pack(padx=20, pady=5)
        self.cb_user.bind('<<ComboboxSelected>>', self.selected_combobox)

        # Set Encryption Key Label
        self.enc_label = tkinter.Label(self.win, bg='pink', text="Set encryption key to the selected user")
        self.enc_label.config(font=('Arial', 12))
        self.enc_label.pack(padx=20, pady=5)

        # Set Encryption Key Input
        self.enc_input = tkinter.Entry(self.win, width=5)
        self.enc_input.pack(padx=20, pady=5)

        # Set Encryption Key Button
        self.enc_button = tkinter.Button(self.win, text="Set Encryption Key", bg='lightblue', command=self.set_enckey)
        self.enc_button.pack(padx=20, pady=5)
        self.enc_button.config(font=('Arial', 12))

        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        # stating that now the gui is done and ready to run
        self.gui_ready = True
        self.win.mainloop()

    # function to set encrytion key for the selected user
    def set_enckey(self):
        selected_user = self.cb_user.get()
        if len(selected_user) == 0:
            message = "No username was chosen"
            self.update_ui(message)
            return
        keystr = self.enc_input.get()
        if keystr.isalpha():
            message = "Input value must be an integer"
            self.update_ui(message)
            return
        elif int(keystr) > 94:
            message = "Can't set key more than 94"
            self.update_ui(message)
            return
        elif keystr == '':
            message = "No key is inserted"
            self.update_ui(message)
            return
        key = int(keystr)
        self.my_keys[selected_user] = key
        message = f"KEY;{self.nickname};{selected_user};{key}"
        self.sock.send(message.encode('ascii'))
        self.update_ui("(Sent encryption key to " + selected_user + ')')
        return

    def check_file_history(self):
        path_name = self.nickname
        path = Path(path_name)
        if path.is_file():
            return True
        return False

    def write_text_history(self, msg):
        with open(self.nickname, 'a') as f:
            f.writelines(msg)
            f.writelines('\n')
        f.close()

    def load_text_history(self):
        text_file = open(self.nickname, 'r')
        stuff = text_file.read()
        self.update_ui(stuff)
        text_file.close()

    # function to receive message and nickname input from user
    def receive(self):
        while True:
            time.sleep(0.1)
            if not self.gui_ready:
                # print("warn: gui not yet done")
                continue
            # empty string to store message that this socket received
            buffer = ''
            try:
                # socket receive something
                received = self.sock.recv(1024).decode('ascii')
                # print(received)
                # store it in buffer variable
                buffer += received
                # and the split it by \n only the first encounter of that special request
                splitted = buffer.split("\n", 1)
                # print(splitted)
                if len(splitted) == 1:
                    continue
                # getting the first index of the splitted string to know if we receive NICK, CHAT, NICKNAMES or KEY
                packet = splitted[0]
                # print(packet)
                buffer = splitted[1].split(';')
                # print(buffer)
                anu = buffer[0]
                # print(anu)
                pisah = packet.split(";")
                # print(pisah)
                cmd = pisah[0]
                # print(cmd)

                if cmd == 'NICK':
                    self.sock.send(self.nickname.encode('ascii'))
                # elif anu == 'USERLIST':
                #     print(anu)
                elif cmd == 'NICKNAMES':
                    usernames = pisah[1:]
                    self.cb_user['values'] = tuple(usernames)
                    if self.cb_user.current() == -1:
                        self.cb_user.current(0)
                elif cmd == 'KEY':
                    from_username = pisah[1]  # sender
                    to_username = pisah[2]  # receiver
                    # if the receiver's name is not "this" then the key will not be distributed to them
                    if to_username != self.nickname:
                        continue
                    key = pisah[3]
                    self.from_keys[from_username] = int(key)
                    self.update_ui(f"Received secret key from {from_username}")
                elif cmd == 'CHAT':
                    sender = pisah[1]
                    message = pisah[2]
                    key = 0
                    if sender not in self.from_keys:
                        # key = 0
                        continue
                    else:
                        key = self.from_keys[sender]
                        message_dec = sender + ": " + algorithm.caesar_dec(message, key)
                        self.update_ui(message_dec)
                        self.write_text_history(message_dec)
                else:
                    self.update_ui(cmd)
            except Exception as ex:
                # self.sock.shutdown(0)
                self.sock.close()
                print('Error', ex)
                break

    # function to update the UI
    def update_ui(self, message):
        self.chat_box.config(state='normal')
        self.chat_box.insert('end', message + "\n")
        self.chat_box.yview('end')
        self.chat_box.config(state='disabled')

    # function that do the action when user press send when they send messages
    def write(self):
        try:
            # user's message input
            message = self.msg_input.get("1.0", 'end-1c')
            if len(message) == 0:
                msg = "No message to send"
                self.update_ui(msg)
                return
            selected_user = self.cb_user.get()
            key = self.my_keys[selected_user]
            # msg = f"CHAT;{self.nickname};{algorithm.caesar_enc(message, key)}"
            msg = "{};{};{}".format("CHAT", self.nickname, algorithm.caesar_enc(message, key))
            self.sock.send(msg.encode('ascii'))
            self.msg_input.delete('1.0', 'end')
        except KeyError as ex:
            print("Error", ex)
        except Exception as ex:
            print("Error", ex)

    # disconnect function
    def stop(self):
        # print(str(self.nickname).strip('\n'))
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)


client = Client(HOST, PORT)
