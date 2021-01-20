import socket
from _thread import *
import sys
import random

client_number = 2
words = ['blue','red','green','pink','white','black']
games = []

class Game:
    perkataan = ""
    jawapan = ""
    guesses = 0
    hurufsalah = 0
    turn = 1
    lock = 0
    full = False

    def __init__(player, perkataan, no_players):
        player.hurufsalah = []
        player.lock = allocate_lock()
        player.perkataan = perkataan
        for i in range(len(perkataan)):
            player.jawapan += "_"
        if no_players == 1:
            player.full = True

    def menangkalah(player):
        if player.guesses >= 6:
            return 'NOPE! You lose the game, GAMEOVERR!'
        elif not '_' in player.jawapan:
            return 'YAYYYY! You win!'
        else:
            return ''

    def guess(player, huruf):
        if huruf not in player.perkataan or huruf in player.jawapan:
            player.guesses += 1
            player.hurufsalah.append(huruf)
            return 'WRONG!'
        else:
            jawapan = list(player.jawapan)
            for i in range(len(player.perkataan)):
                if player.perkataan[i] == huruf:
                    jawapan[i] = huruf
            player.jawapan = ''.join(jawapan)
            return 'Yes! You are correct!'

    def giliran(player):
        if player.turn == 1:
            player.turn = 2
        else:
            player.turn = 1


def Main():
    global client_number
    global words
    host = '192.168.0.4'
    port = 8888


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Host: ' + host + '| Port :' + str(port))


    try:
        s.bind((host, port))
    except socket.error as e:
        print(str(e))
    s.listen(2)


    while True:
        c, addr = s.accept()
        client_number += 1
        print("Connection connected! from: " + str(addr))
        start_new_thread(client_thread, (c,))

def game_status(no_players):
    if no_players == 2:
        for game in games:
            if not game.full:
                game.full = True
                return (game, 2)
    if len(games) < 3:
        perkataan = words[random.randint(0, 5)]
        game = Game(perkataan, no_players)
        games.append(game)
        return (game, 1)
    else:
        return -1

def client_thread(c):
    global client_number

    multiplayer_start = c.recv(1024).decode('utf-8')

    if multiplayer_start == '2':
        x = game_status(2)
        if x == -1:
            send(c, 'server dah penuh!')
        else:
            game, player = x
            send(c, 'Waiting for other player!')

            while not game.full:
                continue
            send(c, 'Game starting!')
            multiplayer_game(c, player, game)

    else:
        x = game_status(1)
        if x == -1:
            send(c, 'server dah penuh!')
        else:
            game, player = x
            one_playerGame(c, game)

def send(c, msg):
    packet = bytes([len(msg)]) + bytes(msg, 'utf8')
    c.send(packet)

def game_result(c, game):
    msg_flag = bytes([0])
    data = bytes(game.jawapan + ''.join(game.hurufsalah), 'utf8')
    gamePacket = msg_flag + bytes([len(game.perkataan)]) + bytes([game.guesses]) + data
    c.send(gamePacket)

def multiplayer_game(c, player, game):
    global client_number

    while True:
        while game.turn != player:
            continue
        game.lock.acquire()

        status = game.menangkalah()
        if status != '':
            game_result(c, game)
            send(c, status)
            send(c, "Game Over!")
            game.giliran()
            game.lock.release()
            break

        send(c, 'Your Turn!')

        game_result(c, game)

        terima = c.recv(1024)
        worddahpakai = bytes([terima[1]]).decode('utf-8')

        send(c, game.guess(worddahpakai))

        status = game.menangkalah()
        if len(status) > 0:
            game_result(c, game)
            send(c, status)
            send(c, "Game Over!")
            game.giliran()
            game.lock.release()
            break

        send(c, "Waiting for other player......")
        game.giliran()
        game.lock.release()

    if game in games:
        games.remove(game)
    c.close()
    client_number -= 1


def one_playerGame(c, game):
    global client_number

    while True:
        game_result(c, game)

        terima = c.recv(1024)
        worddahpakai = bytes([terima[1]]).decode('utf-8')

        send(c, game.guess(worddahpakai))

        status = game.menangkalah()
        if len(status) > 0:
            game_result(c, game)
            send(c, status)
            send(c, "Game Over!")
            break
    games.remove(game)
    c.close()
    client_number -= 1



if __name__ == '__main__':
    Main()
