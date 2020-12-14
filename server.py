import socket
from threading import Thread
from queue import Queue

word = "test"
word_list = list(word)
guessed_index = []

def player(client, status, thread_status, player_num, current_player, current_guess):
    while True:
        if thread_status.qsize() > 0 or status.qsize() == 0:
            continue
        else:
            status_msg = status.get()
            status.put(status_msg)
            if status_msg[:10] == "awaitguess":
                curr_player = current_player.get()
                current_player.put(curr_player)
                if curr_player == player_num:
                    client.sendall(str.encode("startguess"))
                    thread_status.put("done")
                    recv = client.recv(1024)
                    current_guess.put(recv.decode("utf-8"))
                else:
                    client.sendall(str.encode("noturturn" + status_msg[10:]))
                    thread_status.put("done")
            else:
                client.sendall(str.encode(status_msg))
                thread_status.put("done")

def await_thread(message, max_players, curr_player_clear):
    while True:
        if thread_status.qsize() == max_players:
            thread_status.queue.clear()
            status.queue.clear()
            if curr_player_clear:
                current_player.queue.clear()
            print(message)
            break
        else:
            continue


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = "192.168.3.151"
port = 50000

s.bind((ip , port))
s.listen(5)

current_player_num = 0
max_players = 2
players = []
status = Queue()
current_player = Queue()
thread_status = Queue()
current_guess = Queue()
isFinished = False

while True:
    count = 0
    if current_player_num == max_players:
        status.put("gamestart")
        await_thread("All players joined", max_players, False)
        while not isFinished:
            curr_player = (count % max_players) + 1
            current_player.put(curr_player)
            print("Current guesser is {}(player {})".format(players[curr_player - 1], str(curr_player)))
            count += 1
            status.put("awaitguess" + players[curr_player - 1])
            await_thread("All clients received command, awaiting player to guess", max_players, True)
            while True:
                if current_guess.qsize() == 0:
                    continue
                else:
                    guess = current_guess.get()
                    status.put("guessed" + guess + players[curr_player - 1])
                    await_thread("All clients received guess.", max_players, False)
                string_list = []
                for index, i in enumerate(word_list):
                    if i == guess:
                        guessed_index.append(index)
                for index, i in enumerate(word_list):
                    if index not in guessed_index:
                        string_list.append("_")
                    else:
                        string_list.append(i)
                string = ' '.join(string_list)
                if string_list == word_list:
                    status.put("winner"+str(players[curr_player - 1]))
                    await_thread("All clients received final winner.", max_players, False)
                    isFinished = True
                status.put("updated" + string)
                await_thread("All clients received updated word.", max_players, False)
                break
        break
    else:
        c, addr = s.accept()
        addr = "{}:{}".format(addr[0], addr[1])
        recv = c.recv(1024)
        player_name = recv.decode("utf-8")
        players.append(player_name)
        current_player_num += 1
        print("{} has connected. Position in queue: {}".format(player_name, str(current_player_num)))
        c.sendall(str.encode("inqueue" + str(current_player_num)))
        thread = Thread(target=player, args=(c, status, thread_status, current_player_num, current_player, current_guess,))
        thread.start()