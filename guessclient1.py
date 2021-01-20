import socket
import sys


def Main():
    host = "192.168.0.128"
    port = 8888
    s = socket.socket()
    s.connect((host, port))

    print("Playing as Multiplayer? TYPE 'y' or 'n'(y=yes, n=no)")
    print(">>", end='')
    msg = input().lower()

    while 1:
        if msg == 'y' or msg == 'n':
            break
        msg = input('Please enter either y (y=Yes) or n (n=No)')

    if msg == 'y':

        multiplayer_start = '2'.encode('utf-8')
        s.send(multiplayer_start)
        playGame(s)

    else:
        multiplayer_start = '0'.encode('utf-8')
        s.send(multiplayer_start)

        print("Single Player Game has Started")
        playGame(s)


def recv_byte(socket):
    first_byte_value = int(socket.recv(1)[0])
    if first_byte_value == 0:
        x, y = socket.recv(2)
        return 0, socket.recv(int(x)), socket.recv(int(y))
    else:
        return 1, socket.recv(first_byte_value)


def playGame(s):
    print("Guess the Word! CLUE: Colors")
    while True:
        result = recv_byte(s)
        msg_flag = result[0]
        if msg_flag != 0:
            msg = result[1].decode('utf8')
            print(msg)
            if msg == 'server dah penuh!!!' or 'Game Over!' in msg:
                break
        else:
            jawapan = result[1].decode('utf8')
            guesses = result[2].decode('utf8')
            print(" ".join(list(jawapan)))
            print("WRONG Guesses: " + " ".join(guesses) + "\n")
            if "_" not in jawapan or len(guesses) >= 6:
                continue
            else:
                worddahpakai = ''
                valid = False
                while not valid:
                    worddahpakai = input('Huruf untuk diteka: ').lower()
                    if worddahpakai in guesses or worddahpakai in jawapan:
                        print("Error! Huruf " + worddahpakai.upper() + " sudah dipakai!!Please enter another.")
                    elif len(worddahpakai) > 1 or not worddahpakai.isalpha():
                        print("YOU CAN ONLY GUESS USING 1 ALPHABET AT A TIME")
                    else:
                        valid = True
                msg = bytes([len(worddahpakai)]) + bytes(worddahpakai, 'utf8')
                s.send(msg)

    s.shutdown(socket.SHUT_RDWR)
    s.close()


if __name__ == '__main__':
    Main()
