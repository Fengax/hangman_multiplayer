import socket
import time

HOST = "192.168.3.151"
PORT = 50000 # The port used by the server

name = input("Name: ")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(str.encode(name))
    while True:
        recv = s.recv(2048)
        status = recv.decode("utf-8")
        if status[:7] == "inqueue":
            print("You are in queue. Your position is: {}".format(status[7:]))
        elif status == "gamestart":
            print("All players connected, game will begin.")
        elif status == "startguess":
            guess = input("Its your turn! Start guessing: ")
            s.sendall(str.encode(guess))
        elif status[:9] == "noturturn":
            print("Awaiting {}'s guess...".format(status[9:]))
        elif status[:7] == "guessed":
            print("{} guessed {}".format(status[8:], status[7]))
        elif status[:7] == "updated":
            print("The word is: {}".format(status[7:]))
        elif status[:6] == "winner":
            print("{} guessed the word!".format(status[6:]))
        time.sleep(1)