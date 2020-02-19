"""
 Implements a simple socket server

"""

import socket
import threading
from time import gmtime, strftime
from datetime import datetime, timedelta

# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

class User:
    def __init__(self, name, client_connection):
        self.name = name
        self.client_connection = client_connection

    def addRoomMod(self, roomName):
        self.roomsMod.append(roomName)

    def getClientConnection(self):
        return self.client_connection

    def getClientName(self):
        return self.name


class Room:
    def __init__(self, name, private):
        self.name = '#' + name
        self.mods = []
        self.bannedUsers = {}
        self.private = private

    def getRoomName(self):
        return self.name

    def addMod(self, userName):
        self.mods.append(userName)

    def removeMod(self, userName):
        self.mods.remove(userName)

    def getRoomsMod(self):
        return self.mods

    def addBannedUser(self,name,banTime):
        self.bannedUsers[name] = banTime

    def removeBannedUser(self,name):
        self.bannedUsers.pop(name)

    def getBannedUsers(self):
        return self.bannedUsers


geral = Room('geral', False)

rooms = { geral : [] }


def getUserRoom(username):
    for k, v in rooms.items():
        for x in v:
            if username == x.getClientName():
                return k

def getRoomsUsers(client_connection):
    str = ''
    for k, v in rooms.items():
        client_connection.sendall(k.getRoomName().encode())
        for x in v:
            str = ' ' + x.getClientName()
            client_connection.sendall(str.encode())

def sendMsg(client, msg):
    userRoom = getUserRoom(client.getClientName())
    if userRoom != None:
        for k,v  in rooms.items():
            if k.getRoomName() == userRoom.getRoomName():
                for cliente in v:
                    cliente.getClientConnection().sendall(msg.encode())

def sendPrivateMsg(client, msg, clientToSend):
    for k, v in rooms.items():
        for x in v:
            if x.getClientName() == clientToSend:
                x.getClientConnection().sendall(msg.encode())

def move_user(room, client):
    if getUserRoom(client.getClientName()) == room:
        str = 'You are already connected to this room!'
        client.getClientConnection().sendall(str.encode())
        return
    for k, v in rooms.items():
        if k == room:
            for k1, v1 in k.getBannedUsers().items():
                if client.getClientName() == k1:
                    if v1 == -1:
                        str = 'You were banned from this room permanently!'
                        client.getClientConnection().sendall(str.encode())
                        return
                    elif datetime.now() < v1:
                        str = 'You were banned from this room temporarily!'
                        client.getClientConnection().sendall(str.encode())
                        return
                    elif datetime.now() >= v1:
                        k.removeBannedUser(k1)
                        break
    canEnter = False
    if room.private:
        for k, v in rooms.items():
            if k == room:
                for x in k.getRoomsMod():
                    if x == client.getClientName():
                        canEnter = True
    else:
        canEnter = True
    if canEnter:
        for k, v in rooms.items():
            for x in v:
                if client.getClientName() == x.getClientName():
                    rooms[k].remove(x)
                    str = 'You were removed from room: ' + k.getRoomName()
                    client.getClientConnection().sendall(str.encode())
        for k, v in rooms.items():
            if k == room:
                rooms[k].append(client)
                str = 'You moved to room: ' + room.getRoomName()
                client.getClientConnection().sendall(str.encode())
    else:
        str = 'This room is private! You cannot enter here!'
        client.getClientConnection().sendall(str.encode())

def handle_client(user,):
    client_connection = user.getClientConnection()
    name = user.getClientName()
    loginMsg = 'You are now connected, ' + name + '!'
    client_connection.sendall(loginMsg.encode())
    sendMsg(user, name + ' has been connected to #geral')

    while True:
        #Print message from client
        msg = strftime('%H:%M:%S', gmtime()) + ' (' + name + ') ' + client_connection.recv(1024).decode()
        print('Received:', msg)

        aux = msg.split(' ')
        # Check for exit
        if aux[2] == 'exit':
            exitMsg = 'Goodbye ' + name + '!'
            client_connection.sendall(exitMsg.encode())
            break

        elif aux[2] == 'rooms':
            getRoomsUsers(client_connection)

        elif aux[2] == 'create':
            if aux.__len__() == 4 or aux.__len__() == 5:
                roomExists = False
                for k in rooms.keys():
                    if k.getRoomName() == '#' + aux[3]:
                        str = 'Room ' + aux[3] + ' already exists!'
                        client_connection.sendall(str.encode())
                        roomExists = True
                if roomExists == False:
                    room = Room(aux[3], False)
                    if aux.__len__() == 5 and aux[4] == 'priv':
                        room = Room(aux[3], True)
                    else:
                        room = Room(aux[3], False)
                    rooms[room] = [];
                    room.addMod(name)
                    str = 'Room ' + aux[3] + ' has been created'
                    client_connection.sendall(str.encode())
                    move_user(room, user)
        elif aux[2] == 'ban':
            if aux.__len__() == 4 or aux.__len__() == 5:
                if aux[3] != user.getClientName():
                    userToBan = aux[3]
                    userIsMod = False
                    for k, v in rooms.items():
                        if k == getUserRoom(user.getClientName()):
                            for x in k.getRoomsMod():
                                if x == user.getClientName():
                                    userIsMod = True
                                    for y in v:
                                        if y.getClientName() == userToBan:
                                            if aux.__len__() == 5:
                                                banTime = datetime.now() + timedelta(seconds=float(aux[4]))
                                            else:
                                                banTime = -1
                                            v.remove(y)
                                            k.addBannedUser(userToBan, banTime)
                                            str = user.getClientName()+ ' banned ' + userToBan + ' from ' + k.getRoomName()
                                            sendMsg(user, str)
                            if userIsMod == False:
                                str = 'You do not have permission to execute this command'
                                client_connection.sendall(str.encode())
                                break
                else:
                    str = 'You can not banish yourself'
                    client_connection.sendall(str.encode())

        elif aux[2] == 'remove' and aux[3] == 'ban':
            if aux.__len__() == 5:
                if aux[4] != user.getClientName():
                    userIsMod = False
                    banned = False
                    for k, v in rooms.items():
                        if k == getUserRoom(user.getClientName()):
                            for x in k.getRoomsMod():
                                if x == user.getClientName():
                                    userIsMod = True
                                    break
                            if userIsMod == False:
                                str = 'You do not have permission to execute this command'
                                client_connection.sendall(str.encode())
                                break
                            for x in k.getBannedUsers():
                                if x == aux[4]:
                                    banned = True
                                    k.removeBannedUser(aux[4])
                                    str = aux[4] + ' is no longer banned from ' + k.getRoomName()
                                    client_connection.sendall(str.encode())
                                    break
                            if banned == False:
                                str = 'The user is not banned from this room'
                                client_connection.sendall(str.encode())
                else:
                    str = 'You can not remove ban to yourself'
                    client_connection.sendall(str.encode())

        elif aux[2] == 'giveMod':
            if aux.__len__() == 4:
                isMod = False
                userIsMod = False
                for k, v in rooms.items():
                    if k == getUserRoom(user.getClientName()):
                        for x in k.getRoomsMod():
                            if x == user.getClientName():
                                userIsMod = True
                                break
                        if userIsMod:
                            for x in k.getRoomsMod():
                                if x == aux[3]:
                                    isMod = True
                                    str = aux[3] + ' is already a moderator'
                                    client_connection.sendall(str.encode())
                                    break
                            if isMod == False:
                                k.addMod(aux[3])
                                str = user.getClientName() + ' give ' + aux[3] + ' moderator rule!'
                                sendMsg(user, str)
                        else:
                            str = 'You do not have permission to execute this command'
                            client_connection.sendall(str.encode())
                            break

        elif aux[2] == 'remove' and aux[3] == 'mod':
            if aux.__len__() == 5:
                if aux[4] != user.getClientName():
                    userIsMod = False
                    isMod = False
                    for k, v in rooms.items():
                        if k == getUserRoom(user.getClientName()):
                            for x in k.getRoomsMod():
                                if x == user.getClientName():
                                    userIsMod = True
                                    break
                            if userIsMod == False:
                                str = 'You do not have permission to execute this command'
                                client_connection.sendall(str.encode())
                                break
                            if userIsMod:
                                for x in k.getRoomsMod():
                                    if x == aux[4]:
                                        isMod = True
                                        k.removeMod(aux[4])
                                        str = aux[4] + ' is no longer a moderator in the room ' + k.getRoomName() + '!'
                                        client_connection.sendall(str.encode())
                                        break
                            if isMod == False:
                                str = aux[4] + ' is not moderator of the room ' + k.getRoomName() + '!'
                                client_connection.sendall(str.encode())
                                break
                else:
                    str = 'You can not remove permitions to yourself'
                    client_connection.sendall(str.encode())

        elif aux[2] == 'move':
            if aux.__len__() == 4:
                existRoom = False
                for k, v in rooms.items():
                   if k.getRoomName() == '#' + aux[3]:
                        existRoom = True
                        move_user(k, user)
                if existRoom == False:
                    str = 'This room does not exist!'
                    user.getClientConnection().sendall(str.encode())

        elif aux[2] == 'whisper':
            if aux.__len__() >= 5:
                auxMsg = user.getClientName()+' whispered you: '
                for x in aux[4:]:
                    auxMsg += x + ' '

                sendPrivateMsg(user,auxMsg, aux[3])

        else:
            # Return message to other clients
            sendMsg(user,msg)

    # Close client connection
    print(name, ' disconnected...')
    sendMsg(user, name + ' has been disconnected')
    client_connection.close()
    for k,v in rooms.items():
        for cliente in v:
            if cliente.getClientConnection() == client_connection:
                v.remove(cliente)

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
print('Listening on port %s ...' % SERVER_PORT)


def acept_username_thread(connection):
    while True:
        aux = 0
        username = connection.recv(1024).decode()
        if username.split(' ').__len__() > 1:
            aux = 1
            res = 'Invalid username'
            connection.sendall(res.encode())

        for k, v in rooms.items():
            for x in v:
                if x.getClientName() == username:
                    aux = 1
                    res = 'Username is in use'
                    connection.sendall(res.encode())
        if aux==0:
            cliente = User(username, connection)
            # connectedList.append(connection)
            rooms[geral].append(cliente)
            print(username, ' has conected to #geral')
            # Cria thread
            thread = threading.Thread(target=handle_client, args=(cliente,))
            thread.start()
            break

while True:
    # Wait for client connections
    connection, client_address = server_socket.accept()

    # Cria thread
    thread = threading.Thread(target=acept_username_thread, args=(connection,))
    thread.start()

# Close socket
server_socket.close()
